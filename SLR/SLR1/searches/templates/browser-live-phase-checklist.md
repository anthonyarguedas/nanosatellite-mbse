# Shared CfT live-phase safety

## Mode 1 technical development

Do **not** copy or fill out a checklist. Check these facts in memory and run the test:

- canonical CfT is healthy at `127.0.0.1:9222`, versions match, one inert anchor exists, and the OS lease is free;
- no relevant proxy is active when proxy failure is a risk;
- the adapter uses only its owned page and the canonical lease under `caffeinate -dims`;
- the query is a small sentinel and temporary output is under an ignored disposable workspace; and
- no CAPTCHA/challenge interaction, profile rotation, screening, import, or final event is allowed.

The lease runner may write a temporary receipt for cleanup enforcement. Do not index, hash, or copy it into the source packet. After each live invocation, verify the owned page closed, the anchor remains, the lease released, and no orphan remains. Then patch and retest; a failed replay is not a formal run.

## Mode 2 evidence

For a frozen evidence phase, record the formal checks required by its plan:

- exact campaign/attempt identity, source boundary, query/control semantics, and create-only output/receipt paths;
- canonical browser epoch, CfT provenance and matching versions, profile/process assertion, endpoint, anchor, power/sleep protection, and lease acquisition;
- prospective finite source operations, pacing, waits, challenge/busy rules, and cancellation behavior;
- source totals with explicit zero versus `null`, controls, identities, pagination/completeness, and no partial import;
- owned-target closure, baseline preservation, cleanup, lease release, and terminal outcome; and
- immutable evidence paths, hashes, rights classes, and no screening/import/final event.

Run the complete browser phase through:

```text
uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py \
  --owner OWNER --source SOURCE --receipt PATH [--wait SECONDS] \
  [--lease-timeout SECONDS] -- COMMAND...
```

A challenge is never solved, clicked, reloaded, or bypassed. A busy reissue is allowed only by the frozen source policy. Unresolved cleanup keeps supervision active.
