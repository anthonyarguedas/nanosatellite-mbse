# OATD X08 screenshot-coordinate setup stop

- **Session ID:** `S-D09-X08-20260826T085101-0400`
- **Mode:** diagnostic exploration only
- **Lease receipt SHA-256:** `66a8c8a049bc27075bba5cbbc59cc757d2eb2d778af0cc91fe8ff280748d27e6`

One owned page navigated once to the normal home page. The screenshot-based driver stopped before interaction because it incorrectly required the CSS viewport dimensions to equal the retained device-pixel screenshot dimensions. `Advanced search options` was not clicked; submit/reissue counts were zero and total is `null`, not zero. The terminal action journal records `possibly_dispatched=false`.

The outer runner independently verified cleanup, inert-anchor preservation, no orphan, and released lease state. No screening, import, record retention, gate, final event, or native-key/System Information side effect occurred.

**No freeze.** The correction is to map screenshot coordinates into the CSS viewport rather than treating Retina screenshot pixels as CSS coordinates.
