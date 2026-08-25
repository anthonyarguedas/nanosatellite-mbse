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
│   ├── campaign.json                  # checkpointed evidence across immutable attempts
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

Directory names use lowercase task IDs, for example `s-d01-scopus` and `s-l02-esa-indico`. Campaign IDs use `<TASK>-C<NN>-<YYYYMMDDThhmmss-offset>` and immutable attempt IDs use `<TASK>-P<NN>-<YYYYMMDDThhmmss-offset>`.

## Separation rules

1. A pilot is diagnostic only. Set `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false` in its manifest.
2. Never copy a pilot result into `final-events/`, screening data, or the candidate corpus.
3. Keep exact queries in plain UTF-8 files. `translation-spec.json` maps each semantic partition to one or more source-native query cells and records lossless unions.
4. `guideline.md` contains the reusable operating method, not a chronological narration.
5. Pilot manifests and evidence contain observations. Every behavioral claim must be labelled `observed`, `official_documentation`, `inferred`, or `untested`; inferred or untested behavior cannot satisfy acceptance.
6. Record explicit source zero as zero. Access, syntax, transport, pagination, reconciliation, or completeness failures use `null`; never import a partial prefix.
7. Keep restricted or copyrighted captures outside Git when rights require it. Track a safe evidence index, checksum, access classification, and secure-location reference instead.
8. `final-events/` remains empty until task `R-002` is authorized.

## Shared CfT browser live-phase contract

This contract supersedes per-source fresh-browser, profile, port, launcher, and restart guidance. Existing pilot evidence remains immutable historical evidence, not an instruction for a new live phase. Use [`templates/browser-live-phase-checklist.md`](templates/browser-live-phase-checklist.md) for every browser-backed phase.

### Fixed supervisor service

- The browser supervisor alone owns one Chrome for Testing (CfT) process, its persistent profile `~/agent-tools/.browser-profiles/chrome-automation`, and endpoint `127.0.0.1:9222`. There must never be multiple Chrome processes using that profile.
- Pilots and controllers are clients, never browser controllers. They must not launch, stop, restart, force-quit, or configure CfT; copy, rotate, inspect, or extract a profile; or set a browser, profile, endpoint, or port override. If the service is unhealthy, stop before source work and ask the supervisor to resolve it outside an active lease.
- The supervisor owns one protected broker anchor. Clients must not navigate, close, or mutate it. An adapter may create and close only pages it owns. Generic `browser_harness new_tab` is prohibited.

### Offline first, then one leased live phase

Finish offline reading, query generation, source-free adapter tests, and artifact/evidence planning before requesting a lease. Only that offline work may run concurrently. Initially, all browser-backed live phases are globally serialized: exactly one exclusive full-live-phase lease across all sources and domains.

A live phase includes browser health checks, source interaction, any prospectively authorized wait, and target cleanup. For SLR1, `--owner`, `--source`, and `--receipt PATH` are mandatory. Wrap the complete phase—not only the source command—in exactly:

```text
uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py --owner OWNER --source SOURCE --receipt PATH [--wait SECONDS] [--lease-timeout SECONDS] -- COMMAND...
```

`OWNER` identifies the supervised pilot/phase, `SOURCE` is the source ID, and `PATH` is a new immutable receipt path. `COMMAND...` is an adapter client command only. Do not substitute another wrapper, connect to another endpoint, or pass browser/profile/port overrides. The central `127.0.0.1:9222` CfT service is the only browser route.

### Health, provenance, and receipt

Before source navigation and again at cleanup, the supervisor/controller records in the immutable receipt and pilot evidence index:

- lease owner/source/receipt, acquisition and verified release; global pacing decision; and any finite wait policy;
- browser epoch, fixed profile identity/path, confirmation that one CfT process owns the profile, endpoint, and CfT provenance (bundle identity and runtime/on-disk versions);
- version, broker-anchor, and target health before/after; adapter-owned target creation and closure; and no mutation of the broker anchor;
- process-scoped sleep protection, power state, and actual Sleep/Wake check for the phase; and
- supervision, cancellation, cleanup, and terminal outcome.

Never record profile contents, cookies, credentials, or session values. On macOS, keep the lease child under process-scoped `caffeinate -dims`; it does not override clamshell sleep, so keep the lid open. A version/anchor/sleep health failure stops source work. Only the supervisor may repair or restart CfT, outside a lease, producing a new recorded browser epoch.

### Challenge, busy, pacing, and stopping

Classify the condition rather than treating all failures alike:

- A **challenge** is an access-control or verification condition, including CAPTCHA, login, or anti-automation interstitial. Do not solve, evade, bypass, or retry it automatically.
- A **busy** condition is an ordinary capacity, queue, rate-limit, or temporary-service response that is not an access-control challenge.

In either case preserve the same adapter-owned tab. A passive wait is allowed only when a prospectively authorized, finite policy records its maximum duration and cadence. A same-tab busy reissue is an internal technical retry only when that policy also records its fixed request limit, delays, and attempted/completed counts; challenge states are never reissued. Otherwise, or when the finite policy expires, request human interaction or stop. Domain pacing is global across sources; a new lease or source ID never resets it. Never rotate profiles or use a fresh browser to escape a condition.

A stopped live attempt does not reissue its failed source operation. A separate source-free diagnosis may immediately inspect safe evidence, static code, or local tests. The controller may allocate a bounded technical corrective attempt under the same campaign without human authorization when the change preserves review semantics and evidence accounting. Human authorization is required only for a `human_methodological` decision that can affect the underlying literature review. Prospectively authorized finite passive waits and internal readiness retries may remain within the current phase.

A deterministic source-free setup or preflight failure is not a source result, a successful safe disposition, or a reason to abandon the pilot. Fix and retest it before source work. Complete these checks before allocating an attempt ID whenever possible. If an ID was already allocated, preserve that setup incident immutably with `allocation.source_phase_started=false`, zero source operations, no lease/browser claim, and no source-gate evidence. It does not consume the finite enacted source-phase attempt budget; the controller must patch the behavior-preserving defect and may prospectively allocate a new technical attempt. Never report a safe stop as satisfactory progress when the requested capability remains untested.

### Cancellation and reporting

A user/operator termination is `cancelled`, not a provider failure. A live executor must remain an attached, supervised child for the entire lease; it must never be detached or backgrounded. Detached subagents are allowed only for source-free offline work. On cancellation, the controller cancels and collects every child, stops source-writing, verifies closure of the adapter-owned target and preservation of the broker anchor, and verifies lease release from the receipt before ending supervision. If cleanup cannot yet be verified, keep supervision active and report that unresolved cleanup; never leave an orphan able to write to the source packet.

Keep a unique immutable attempt receipt even when the terminal outcome is blocked, failed, or cancelled. Maintain `campaign.json` against [`schemas/pilot-campaign.schema.json`](schemas/pilot-campaign.schema.json): carry forward exact-hash evidence for unaffected passed gates, and invalidate only the failed gate and its declared dependents. Describe the terminal blocker precisely; a late optional or technical gate failure does not erase earlier successful gates or make the whole provider "inaccessible." Final searches remain fail-closed: a blocked, failed, or cancelled event imports no partial prefix.

## Required guideline sections

Use [`templates/source-guideline.md`](templates/source-guideline.md). Direct-source acceptance requires guidance for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. Local-source acceptance requires complete candidate and tag rules for P, E, M, `G_model`, `G_structure`, C1, R, and T2.

## Checkpointed campaign lifecycle

Controllers use [`templates/pilot-controller-prompt.md`](templates/pilot-controller-prompt.md); attempt subagents use [`templates/source-pilot-prompt.md`](templates/source-pilot-prompt.md). One source campaign can contain multiple immutable attempts. Browser-backed live phases additionally use the global lease above.

1. **Plan and source-free gate:** define stable capability-gate IDs and dependencies, finite technical-correction bounds, source-operation limits, and the review semantics that must not change. Run deterministic query-byte, CLI, adapter, output-path, and infrastructure checks before allocating an attempt ID whenever possible. Patch technical failures until this gate passes; a safe failure is not readiness.
2. **Attempt:** after the source-free gate passes, execute one diagnostic scope under a new immutable pilot ID. Stop that source operation on failure; never overwrite or reinterpret the attempt. If an already allocated ID stops before any source phase, record `source_phase_started=false` and preserve it without charging the enacted source-phase budget.
3. **Checkpoint:** update `campaign.json`. Preserve unaffected passed gates by exact evidence path and SHA-256. A failed gate invalidates only itself and declared dependents.
4. **Technical correction:** the controller must diagnose and fix demonstrated source-free or live implementation defects, commit behavior-preserving code, rerun focused tests, and allocate a bounded `technical_corrective` attempt without human authorization. Parser/selector robustness, query-byte/CLI consistency, output safety, browser health/restart, target cleanup, observability, passive waits, and validation packaging are technical only when they do not alter review behavior. A technical safe stop is an incident to repair, not campaign completion.
5. **Methodological decision:** ask the review owner only when a proposed change can affect the literature review: concepts or query semantics, source/field boundary, date/language/content limits, or identity/capture/completeness rules affecting recall or PRISMA accounting. Record it as `human_methodological`.
6. **Accept and integrate:** when every required gate passes under the existing protocol and no methodological decision is pending, the controller may accept and commit the campaign. If a methodological change was required, its human decision must be recorded first. Pin external implementations and then reconcile `search-log.md`, the Part 2 source index, and `TASKS.md` serially.

When date controls need testing before `P-001`, use the pilot execution date as a clearly labelled diagnostic upper bound. `P-001` remains required only before the first final search; a pilot bound is never the common cutoff and pilot records are never imported.

## Campaign acceptance gate

The controller accepts a campaign only after:

- the campaign and every immutable attempt validate;
- every required capability gate passes with evidence, including source boundary, interface, fields, controls, expansion, controlled/indexed terms, date/language handling, limits, retrieval, stable identity, completeness, and failure behavior;
- every direct partition or local rule has an exact specification and evidence linkage;
- carried-forward evidence is hash-bound, reusable, and unaffected by later code or semantic changes;
- no screening or candidate import occurred;
- the reusable guideline distinguishes observed behavior, documentation, inference, and remaining uncertainty;
- every `human_methodological` decision is resolved by the review owner, while `controller_technical` decisions require no human authorization;
- any approved semantic change is committed to the protocol before a final search; and
- the acceptance commit records decisions and pins implementations without a separate approval-hash ledger.

## Subagent write boundary

A source-pilot subagent may edit only its assigned source packet and, when explicitly authorized, source-specific scripts under `SLR/SLR1/scripts/`. It must not edit `TASKS.md`, `search-log.md`, any `protocol*.md`, dictionaries, crosswalks, schemas, another source packet, or `final-events/`.
