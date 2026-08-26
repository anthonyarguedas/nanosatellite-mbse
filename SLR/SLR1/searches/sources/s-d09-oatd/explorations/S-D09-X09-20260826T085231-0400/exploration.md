# OATD X09 home-activated composer and submit

- **Session ID:** `S-D09-X09-20260826T085231-0400`
- **Mode:** diagnostic exploration only; no gate claim
- **Lease receipt SHA-256:** `c823ab85d55c0bd4ae380c7ca96e027f4e6b1c83eb9075c7cbd94a9be1c46e75`

## Live observation

One owned page navigated once to `https://oatd.org/`. Using the immediately retained screenshot mapped into CSS viewport coordinates, the driver clicked the visible source-owned **Advanced search options** label exactly once. This revealed the complete advanced form on the same home page without challenge or pre-submit busy state.

The visible canonical GET form had one `box1`, one `field1`, one `title` option, and one visible native submitter. The driver filled exact `CubeSat AND SysML`, selected `title`, required exact readback, wrote a durable pre-click intent, and clicked the native submitter once. No manual reissue occurred.

The submit transitioned to the normal `/oatd/search` route but immediately rendered OATD's ordinary **Please slow down** busy page. The bounded post-submit projection therefore records `total=null`, not zero, with zero retained records. This session proves the operator-reported home-entry recipe and the visible title submission mechanics, but not aggregate reconciliation.

The append-only action journal records one intent, one dispatched submit, and terminal `post_submit_busy`. The outer lease independently verified cleanup, inert-anchor preservation, no orphan, and release. No screening, import, gate, final event, or native-key/System Information side effect occurred.

## Working recipe and handoff

Live-proven steps are: home page → visible **Advanced search options** → same-page visible advanced form → exact title readback → one native submit. The implementation must use this route instead of direct composer navigation and must treat `/oatd/search` as the expected post-submit result route. A later paced X should combine this entry recipe with the existing finite 30/60-second post-submit busy policy.

**P05 remains held.** Aggregate/native-zero reconciliation is still required before evidence mode.
