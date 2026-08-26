# IEEE year-control exploration

- **Session ID:** `S-D03-X01-20260825T201925-0400`
- **Source:** IEEE Xplore
- **Started / ended:** 2026-08-25T20:20:23-04:00 / 2026-08-25T20:29:59-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `70eaedb37892ad3d69a1cfd0eea56f3a5f2c9da3383b40bcd397cce0e4879cbe`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** technically blocked before Year Range Apply; owned-page cleanup and lease release were verified

## Question and starting state

P06 had observed five cards beside a singleton summary after Year Range Apply. X01 used the non-partition count-only sentinel `("All Metadata":"CubeSat") AND ("All Metadata":"SysML")` to inspect the live summary, controls, and full post-Apply transition without rerunning A1 or another partition.

## Real-page observations

One owned page opened the normal rendered search route. It had the exact query URL echo, 25 visible cards, one visible Dashboard header, and one visible ranged-summary `span` inside that header. No loading marker, challenge, source error, duplicate summary candidate, or open shadow root was observed before Apply. Page-size and Relevance selections existed in the component tree but were not visible at the captured viewport; one active page control was visible.

The visible controls were uniquely mapped as `input[aria-label='Enter start year of range']`, `input[aria-label='Enter end year of range']`, and `#Year-apply-btn`. Framework fill, visible keyboard fill/blur, and the native input setter with `input`, `change`, and `blur` events all left the requested end year `2026` exact but did not retain requested start year `2011`; the rendered input showed `2012`. Apply remained disabled. It was not clicked or coerced.

The operation therefore stopped before the loading/hydration transition. The prior five-card/singleton contradiction was neither reproduced nor disproved. The retained projections contain only structural categories, control readback classes, and counts; no raw DOM or result metadata was retained. One restricted screenshot was kept for the control-state diagnosis. The page was closed without selecting another target, and the lease runner independently recorded `child_exit_code=0`, `cleanup=verified-clean`, and `state=released`. The exact phase contained zero Sleep/Wake/DarkWake events under `caffeinate -dims`.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Opened the sentinel on the normal rendered search route and mapped summary/year controls. | yes—one query navigation | none | Ready ranged result state; 25 visible cards. |
| 2 | Filled 2011–2026 through framework-managed visible inputs. | no | none | Start readback mismatched; end exact; Apply disabled. |
| 3 | Retried only local control event mechanics with keyboard/blur and native setter events; no navigation or Apply. | no | none | Start still displayed 2012; Apply remained disabled. |
| 4 | Stopped rather than coercing a disabled control or changing the diagnostic bound. | no | no justified patch | No post-Apply transition occurred. |

## Working interaction recipe

The normal query route, one visible ranged summary under `h1.Dashboard-header`, and the three year-control selectors above are live-observed. A working 2011–2026 Apply recipe is **not** established for this sentinel. The UI's 2012 start readback must not be silently treated as equivalent to requested 2011.

## Implementation

- **Adapter/helper commit inspected:** `1d7474ccf4fa94958e85bf765734adc6fb7372b9` in the isolated worktree; IEEE code unchanged
- **Technical patch:** none; the post-Apply state was not reached, so no selector/wait change was justified
- **Minimum launch check:** adapter `--help` succeeded; no broad suite was run
- **Remaining unknowns:** why this result set rejects 2011, whether another non-partition sentinel can retain the diagnostic bound, and the complete loading/summary/card transition after one valid Apply

## Proposed evidence attempt

**Not frozen.** Evidence mode remains prohibited because X01 did not demonstrate Year Range Apply or a reconciled post-Apply result. A later exploration should choose a declared non-partition sentinel whose visible lower-bound control can retain 2011, require exact 2011/upper-year readback, click Apply exactly once, and poll the same page for at most 60 seconds while recording loading, all summary grammars/visibility, card count, query/range echoes, page-size/page/Relevance controls, and stable reconciliation. Only after that route works may one deterministic year/content/language/completeness evidence attempt be proposed; failures remain `total=null` with no prefix.
