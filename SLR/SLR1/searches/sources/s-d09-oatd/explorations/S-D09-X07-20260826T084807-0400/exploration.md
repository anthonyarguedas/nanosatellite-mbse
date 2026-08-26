# OATD X07 exact-text control attempt

- **Session ID:** `S-D09-X07-20260826T084807-0400`
- **Mode:** diagnostic exploration only
- **Lease receipt SHA-256:** `4328c64966a91746e2652b1a4195c9b437914726851345ace3319ac489661362`

One owned page navigated once to the normal home page and retained a restricted screenshot. A Playwright exact-text locator for `Advanced search options` returned zero actionable visible candidates even though the split/static label was visibly rendered. The control was not activated, no composer control was changed, and no native submit or reissue occurred. Total is `null`, not zero.

The direct child exited zero. Its immediate wrapper-object page-list comparison did not verify closure, but the canonical lease runner independently recorded `cleanup=verified-clean`, preserved the inert anchor, found no orphan, and released the lease. No native-key/System Information side effect occurred.

**No freeze.** A later X must use a screenshot-led visible interaction or a semantic resolver that handles the source's split/static label.
