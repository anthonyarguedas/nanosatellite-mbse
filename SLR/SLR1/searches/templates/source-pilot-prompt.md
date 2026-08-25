# Source-pilot subagent contract

You are assigned exactly one SLR1 source-pilot task. Read `SLR/SLR1/AGENTS.md`, all of `SLR/SLR1/searches/README.md`, `SLR/SLR1/searches/templates/browser-live-phase-checklist.md` when browser-backed, the relevant task in `SLR/SLR1/TASKS.md`, and every linked protocol section before acting.

Constraints:

- This is a focused diagnostic pilot, not a final search and not screening. Use only the normal authorized interface or prospectively validated public/native route; never bypass access controls.
- Finish all offline reading, query generation, source-free adapter tests, and artifact/evidence planning before a browser lease. Only source-free offline work may run concurrently.
- The supervisor owns the sole shared CfT process, profile `~/agent-tools/.browser-profiles/chrome-automation`, endpoint `127.0.0.1:9222`, and protected broker anchor. You are a client, never a browser controller: do not launch, stop, restart, configure, copy, rotate, inspect, or extract the browser/profile; do not override its profile or port.
- For every browser-backed live phase, obtain controller-supplied explicit `OWNER`, `SOURCE`, immutable receipt `PATH`, global-pacing decision, and any finite preauthorized wait policy. Run the entire phase only through:

  ```text
  uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py --owner OWNER --source SOURCE --receipt PATH [--wait SECONDS] [--lease-timeout SECONDS] -- COMMAND...
  ```

  Do not use another endpoint or wrapper. Generic `browser_harness new_tab` is prohibited. The adapter may create and close only its own page; never mutate the broker anchor.
- Stop before source work if the controller has not recorded shared-CfT epoch/profile identity and provenance, version/anchor/sleep health, and the single-process/profile assertion. Do not close the lid.
- Test current behavior; do not treat existing adapters, prior diagnostics, or model memory as proof. Determine whether the source has a genuine controlled vocabulary or distinct indexed-term field. Where available, inspect scope, hierarchy, and known-record descriptors, and test them only as OR supplements to the mapped free-text concept; otherwise document that none is usable.
- A **challenge** (CAPTCHA, login, verification, or anti-automation) is not **busy** (ordinary capacity, queue, rate-limit, or temporary service condition). In either case keep the same owned page. Never evade access controls, rotate profiles, or create a fresh page to retry. Passively wait only under the predeclared finite policy; otherwise request human action and stop source work.
- A user/operator stop is `cancelled`, not provider failure. Remain an attached supervised live child; do not detach or background it. On cancellation, the controller must cancel/collect children and verify owned-page cleanup, anchor preservation, lease release, and stopped source-writing before ending supervision. Detached subagents may do source-free offline work only.
- A stopped live attempt never reissues its failed source operation. A source-free diagnosis may begin immediately. The controller may allocate a bounded behavior-preserving technical corrective attempt under the same campaign without human authorization. Ask the review owner only for methodological changes that can affect review scope, recall, limits, semantics, capture/completeness, or PRISMA accounting.
- Save only inside the assigned source packet. Do not edit shared integration files. Do not retain or classify records beyond the minimum diagnostic metadata needed to test totals, pagination, stable identity, and completeness.
- Mark unknown behavior unknown. Produce a capability/carry-forward handoff with exact evidence paths and hashes; the controller alone updates `campaign.json`, carrying forward unaffected passed gates and invalidating only the failed gate and declared dependents. Do not call a provider wholly inaccessible when a late optional or technical gate failed. Record `code_issue` as `true`, `false`, or `unresolved`. Do not patch a demonstrated defect unless separately assigned as the source-free code-fix subagent.
- End after the assigned immutable attempt. Do not self-accept the campaign, start another source, update central status, or commit. The controller owns checkpointing and may allocate a new technical corrective attempt within its predeclared campaign bounds; human authorization applies only to `human_methodological` changes.
- Ask for a final summary containing: attempt status/terminal outcome; passed, failed, and dependent capability gates; carry-forward eligibility; files changed; tested and blocked requirements; immutable evidence and receipt paths; `code_issue`; cancellation/cleanup state; technical decisions for the controller; methodological decisions, if any, for the review owner; semantic/protocol impact; and the smallest next action.
