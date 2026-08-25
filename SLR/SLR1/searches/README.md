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
│   ├── explorations/<session-id>/     # iterative agent-driven interface discovery
│   │   ├── exploration.md
│   │   └── restricted-evidence-index.json
│   └── pilots/<pilot-id>/             # deterministic evidence-mode attempts only
│       ├── manifest.json
│       ├── observations.md
│       └── evidence-index.json
└── final-events/                       # untouched until R-002
```

Directory names use lowercase task IDs, for example `s-d01-scopus` and `s-l02-esa-indico`. Exploration sessions use `<TASK>-X<NN>-<YYYYMMDDThhmmss-offset>` and never count as pilots. Campaign IDs use `<TASK>-C<NN>-<YYYYMMDDThhmmss-offset>` and immutable evidence-attempt IDs use `<TASK>-P<NN>-<YYYYMMDDThhmmss-offset>`.

## Separation rules

1. Exploration and pilot work are diagnostic only. Exploration sessions have no campaign manifest; evidence-mode pilots set `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false`.
2. Never copy an exploration or pilot result into `final-events/`, screening data, or the candidate corpus.
3. Keep exact queries in plain UTF-8 files. `translation-spec.json` maps each semantic partition to one or more source-native query cells and records lossless unions.
4. `guideline.md` contains the reusable operating method, not a chronological narration.
5. Exploration logs may guide implementation but cannot satisfy acceptance. Evidence-mode pilot manifests contain acceptance observations. Every behavioral claim must be labelled `observed`, `official_documentation`, `inferred`, or `untested`; inferred or untested behavior cannot satisfy acceptance.
6. Record explicit source zero as zero. Access, syntax, transport, pagination, reconciliation, or completeness failures use `null`; never import a partial prefix.
7. Keep restricted or copyrighted captures outside Git when rights require it. Track a safe evidence index, checksum, access classification, and secure-location reference instead.
8. `final-events/` remains empty until task `R-002` is authorized.

## Shared CfT browser live-phase contract

This contract supersedes per-source fresh-browser, profile, port, launcher, and restart guidance. Existing pilot evidence remains immutable historical evidence, not an instruction for a new live phase. Use [`templates/browser-live-phase-checklist.md`](templates/browser-live-phase-checklist.md) for every browser-backed phase.

### Fixed supervisor service

- One supervisor-managed Chrome for Testing (CfT) process owns the dedicated pilot profile `~/agent-tools/.browser-profiles/chrome-automation` and endpoint `127.0.0.1:9222`. There must never be multiple Chrome processes using that profile.
- Attempt executors are clients, never browser controllers. They must not launch, stop, restart, force-quit, or configure CfT; copy, rotate, inspect, or extract a profile; or set a browser, profile, endpoint, or port override. An assigned campaign controller may perform only the bounded canonical reconciliation described below, outside a lease; it may not perform manual process/profile administration.
- The supervisor owns one protected broker anchor. Clients must not navigate, close, or mutate it. An adapter may create and close only pages it owns. Generic `browser_harness new_tab` is prohibited.

Because this CfT installation and profile are dedicated to these pilots, an assigned controller need not wait for a separate supervisor round trip when the read-only status is unhealthy. Outside any lease, and only after status proves the OS lease free and no guardian/orphan alive, the controller may run the canonical `start_chrome.py --wait 30` reconciliation under `caffeinate -dims`. That command may reconcile the existing canonical process, recreate one inert anchor, write a new epoch receipt, or launch the canonical process if absent. The controller must then require healthy status, one inert anchor, matching versions, the canonical profile/endpoint, and a free lease before source work. It must not kill Chrome, manipulate the profile, choose another process/endpoint, or use this allowance during or to escape a source condition.

### Live-first validation, then one leased live phase

Apply the normative [`two-mode source-interface policy`](two-mode-validation-policy.md); it supersedes broader offline-preflight language in older source plans. Pilot value comes from observed behavior on the current real interface. Before requesting a lease, do only the minimum source-free work needed to avoid a malformed or destructive run: read the exact plan; verify query bytes; ensure the command imports/starts; reserve create-only outputs; validate the manifest/receipt shape; and check browser health. Do **not** make a large focused or full regression suite, broad fixture expansion, repeated hash audit, lint run, or duplicate validator run a routine prerequisite for a live pilot or technical retry. Run only the smallest tests directly covering code changed for safety or the specific observed failure. Full suites are deferred until a live route is stable and the implementation is being accepted or merged.

Only source-free work may run concurrently. Browser-backed live phases remain globally serialized: exactly one exclusive full-live-phase lease across all sources and domains.

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

Never record profile contents, cookies, credentials, or session values. On macOS, keep the lease child under process-scoped `caffeinate -dims`; it does not override clamshell sleep, so keep the lid open. A version/anchor/sleep health failure stops source work. The supervisor—or an assigned controller using only the bounded canonical reconciliation above—may restore CfT outside a lease, producing a new recorded browser epoch.

### Challenge, busy, pacing, and stopping

Classify the condition rather than treating all failures alike:

- A **challenge** is an access-control or verification condition, including CAPTCHA, login, or anti-automation interstitial. Do not solve, evade, bypass, or retry it automatically.
- A **busy** condition is an ordinary capacity, queue, rate-limit, or temporary-service response that is not an access-control challenge.

In either case preserve the same adapter-owned tab. A passive wait is allowed under a finite controller-recorded maximum and cadence. A transient challenge may be left untouched and passively polled on the same page; never click, reload, solve, or bypass it. A same-tab busy reissue remains bounded and auditable. Domain pacing is global across sources; a new lease or source ID never resets it. Never rotate profiles or use a fresh browser to escape a condition.

A live technical failure triggers exploration mode. Prefer agent-driven observation of the owned page—screenshots, semantic DOM inspection, visible interaction, and bounded state polling—over guessing from a collapsed error class. Do not allocate successive evidence attempts to debug selectors. Patch and live-validate the route in one exploration session; return to evidence mode only after the interaction recipe and implementation work on the real page. Human authorization is required only for a `human_methodological` change affecting the review.

A deterministic source-free setup or preflight failure is not a source result, a successful safe disposition, or a reason to abandon the pilot. Fix and retest it before source work. Complete these checks before allocating an attempt ID whenever possible. If an ID was already allocated, preserve that setup incident immutably with `allocation.source_phase_started=false`, zero source operations, no lease/browser claim, and no source-gate evidence. It does not consume the finite enacted source-phase attempt budget; the controller must patch the behavior-preserving defect and may prospectively allocate a new technical attempt. Never report a safe stop as satisfactory progress when the requested capability remains untested.

### Cancellation and reporting

A user/operator termination is `cancelled`, not a provider failure. A live executor must remain an attached, supervised child for the entire lease; it must never be detached or backgrounded. Detached subagents are allowed only for source-free offline work. On cancellation, the controller cancels and collects every child, stops source-writing, verifies closure of the adapter-owned target and preservation of the broker anchor, and verifies lease release from the receipt before ending supervision. If cleanup cannot yet be verified, keep supervision active and report that unresolved cleanup; never leave an orphan able to write to the source packet.

Keep a unique immutable attempt receipt even when the terminal outcome is blocked, failed, or cancelled. Maintain `campaign.json` against [`schemas/pilot-campaign.schema.json`](schemas/pilot-campaign.schema.json): carry forward exact-hash evidence for unaffected passed gates, and invalidate only the failed gate and its declared dependents. Describe the terminal blocker precisely; a late optional or technical gate failure does not erase earlier successful gates or make the whole provider "inaccessible." Final searches remain fail-closed: a blocked, failed, or cancelled event imports no partial prefix.

## Required guideline sections

Use [`templates/source-guideline.md`](templates/source-guideline.md). Direct-source acceptance requires guidance for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2. Local-source acceptance requires complete candidate and tag rules for P, E, M, `G_model`, `G_structure`, C1, R, and T2.

## Exploration-to-evidence lifecycle

Controllers use [`templates/pilot-controller-prompt.md`](templates/pilot-controller-prompt.md); exploration agents use [`templates/browser-exploration-prompt.md`](templates/browser-exploration-prompt.md); evidence agents use [`templates/source-pilot-prompt.md`](templates/source-pilot-prompt.md). Exploration precedes the checkpointed campaign when the interface is unknown or technically failing. Browser-backed live phases additionally use the global lease above.

1. **Choose mode:** use exploration for an unknown/failing interface; use evidence only for a route already demonstrated live.
2. **Explore:** allocate one `X` session, pass the minimum launch gate, and iteratively inspect, patch, and retest the owned real page. Keep a concise exploration log and restricted screenshots/DOM projections. Do not update capability gates.
3. **Freeze:** after the route works, pin the interaction recipe, adapter/helper commit, query/control semantics, expected evidence, and bounded evidence plan.
4. **Evidence attempt:** allocate one immutable `P` attempt and execute the frozen deterministic plan. Preserve the attempt on any failure; a technical failure returns the source to exploration rather than spawning a chain of evidence attempts.
5. **Checkpoint or decide:** update `campaign.json` only from evidence-mode observations. Carry forward unaffected passed gates by exact path/hash. Ask the review owner only for methodological changes affecting concepts, scope, limits, recall, identity/capture/completeness meaning, or PRISMA accounting.
6. **Accept and integrate:** when every required evidence gate passes and no methodological decision is pending, accept and commit the campaign, pin implementations, then reconcile `search-log.md`, the Part 2 source index, and `TASKS.md` serially.

When date controls need testing before `P-001`, use the pilot execution date as a clearly labelled diagnostic upper bound. `P-001` remains required only before the first final search; a pilot bound is never the common cutoff and pilot records are never imported.

## Campaign acceptance gate

The controller accepts a campaign only after:

- any exploratory interface work is separately logged and the accepted campaign pins the frozen interaction recipe/implementation derived from it;
- the campaign and every immutable evidence attempt validate;
- every required capability gate passes with evidence, including source boundary, interface, fields, controls, expansion, controlled/indexed terms, date/language handling, limits, retrieval, stable identity, completeness, and failure behavior;
- every direct partition or local rule has an exact specification and evidence linkage;
- carried-forward evidence is hash-bound, reusable, and unaffected by later code or semantic changes;
- no screening or candidate import occurred;
- the reusable guideline distinguishes observed behavior, documentation, inference, and remaining uncertainty;
- every `human_methodological` decision is resolved by the review owner, while `controller_technical` decisions require no human authorization;
- any approved semantic change is committed to the protocol before a final search; and
- the acceptance commit records decisions and pins implementations without a separate approval-hash ledger.

## Subagent write boundary

An exploration subagent may edit its assigned source packet, source-specific review scripts, and an explicitly assigned isolated `agent-tools` worktree; it records no campaign gate. An evidence-pilot subagent may edit only its assigned evidence packet and may not patch the implementation during the attempt. Neither role may edit `TASKS.md`, `search-log.md`, protocols, dictionaries, crosswalks, schemas, another source packet, or `final-events/`.
