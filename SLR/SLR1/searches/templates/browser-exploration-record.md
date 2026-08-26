# Browser exploration run record

- **Logical run ID:** `TASK-ERUN-NN` or restricted controller reference
- **Session IDs:** `TASK-XNN-TIMESTAMP`, `TASK-XNN-TIMESTAMP`, ...
- **Source / exact boundary:** `REPLACE`
- **Started / ended:** `REPLACE`
- **Controller / interactive agent:** `REPLACE`
- **Lease and cleanup receipts:** `REPLACE`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Run status:** `working` / `deferred` / `exhausted` / `safety_stop` / `active_checkpoint`

## Question and starting state

What live technical behavior was unknown or failing? Keep methodological questions separate.

## Lightweight session ledger

| Session | Visible route/action | Source submits/reissues | Aggregate / zero / null | Patch or hypothesis | Cleanup/release | Next iteration |
|---|---|---:|---|---|---|---|
| `XNN` | REPLACE | REPLACE | REPLACE | REPLACE | verified / unresolved | REPLACE |

Record this minimum ledger immediately after each live segment. Raw screenshots, events, DOM projections, and source diagnostics remain restricted and create-only. Do not delay a safe next technical iteration for exhaustive prose, repeated hashes, or a commit per failed selector.

## Real-page observations and state machine

Summarize source-owned routes, semantic controls, hydration/loading states, challenge/busy behavior, totals, identities, and pagination relevant to the recipe. Do not retain credentials, cookies, session tokens, candidate content, or raw opaque routes.

## Iterations and implementation

Describe the plausible options tried, why each failed or succeeded, bounded patches, focused changed-path checks, and live replay outcomes. A single collapsed error or failed replay is not exhaustion.

- **Current adapter/helper commit and hash:** `REPLACE`
- **Minimal changed-path check:** `REPLACE`
- **Successful automated live replay:** `yes` / `no`
- **Remaining unknowns or blocker owner/next condition:** `REPLACE`

## Working recipe or terminal blocker

For `working`, list the exact visible source-owned steps and state assertions demonstrated by the current automation. For `deferred`, state the challenge/busy/cooldown/access/setup/methodological condition and owner. For `exhausted`, list the source-owned routes, semantic locators, and state hypotheses actually tried. For `safety_stop`, identify the unresolved cleanup/lease/browser/proxy condition.

## Proposed evidence attempt

Complete this section only when the current implementation has successfully replayed live. State the exact deterministic capability, query, controls, expected total/identity/coverage evidence, operation cap, and failure rules. Exploration itself passes no gate.
