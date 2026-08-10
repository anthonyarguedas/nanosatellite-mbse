# Version-1.3 reusable-artifact search-design adjudication

**Date:** 2026-08-10
**Classification:** prospective protocol/search design only
**Assessment:** model-assisted; not a human information-specialist review; no screening or record assessment

A focused subagent compared only no-screening source totals and opaque-ID set arithmetic for the core Stream-B, precise-artifact, central-asset, and tailoring probes. It did not inspect titles, abstracts, authors, metadata content, full text, eligibility, or evidence. The integrated protocol and query plan—not the subagent report—are authoritative.

## Decisions retained

1. **Reject the unsplit `P AND G AND R_ALL` query as final logic.** Architecture-bearing phrases such as `reference architecture` can supply their own `architecture` relation token. Its observed additions remain valid retrieval diagnostics, but not support for that Boolean interpretation.
2. **Use relation-free precise G1/G2 partitions.** Complete artifact phrases bound recall without making metadata relation wording mandatory. Scopus and IEEE relation-free pilots produced opaque additions beyond fresh B1∪B2 sets. A separately validated architecture-safe split remains an optional precision fallback, not a replacement.
3. **Use a separate conservative C1 partition.** C1 contains complete reference/system-reference model, model-library, model-pattern, model-profile, SysML-profile, and model-coupled domain-specific modeling-language forms; bare ambiguous terms are prohibited. Scopus, IEEE, and a reconciled Wiley pilot produced opaque additions.
4. **Use a separate model/architecture-coupled T2 partition where it is not structurally contained in core B.** T2 differs from the superseded T1 subset probe by replacing B2's relation gate with a finite tailoring block coupled to model/architecture. Scopus and IEEE produced additions. ESA and NTRS core implementations are already `P AND M` without R, so T2 is a local tag there.
5. **Keep every expansion separate from eligibility and grading.** Retrieval cannot establish an EPS thread, reusable artifact, lineage, applicability envelope, tailoring application, or A/E/C/T/P/I gate.

## Parent-agent conservative resolutions

The adjudication subagent proposed dropping source partitions whose dated pilot delta was zero and delaying partitions when a browser control failed. The integrated version-1.3 plan is more conservative about future recall:

- **NTRS:** retain all finite P×G and P×C1 cells in the clean final rerun despite dated G-only/C1-only zeros. A pilot zero is not structural containment or term equivalence, and NTRS can add older records retrospectively. A final vocabulary audit further retained all ten source-representable P forms; the final matrix is 180 core + 250 G + 230 C1 = 660 cells; T2 remains a core-union tag.
- **ESA:** a complete zero-network rematch of the preserved attachment-first census was available to the parent and superseded the subagent's “cache unavailable” premise. The final matcher uses relation-free complete G/C1 artifacts per route and retains the independent-R subset and T2 as tags. A clean fresh census is still mandatory for discovery.
- **Browser sources:** access, refinement, and total-change failures are retained as failures, not recoded as zeros or grounds to erase prospectively specified queries. The final run must meet each source's normal controls and complete-retrieval rules or report a source failure.

## Final read-only consistency audit and resolution

A separate final read-only subagent audit identified three clarity/reproducibility issues, all resolved before freeze: (1) the plan now defines bibliographic core B explicitly as B1∪B2 and scopes optional R only to exact-artifact expansions; (2) NTRS now preserves ten source-representable P forms rather than asserting unvalidated equivalence, increasing the mandatory matrix to 660 cells; and (3) the plan links the separate tracked 13-case route/attachment aggregation suite in addition to the 19-case base matcher suite. The audit inspected design artifacts only and did not access pilot/candidate records.

## Final logical design

Here `B_core` is the retained bibliographic B1∪B2 union (`P∧M_high` plus `P∧M_broad∧R`) or the local ESA/NTRS `P∧M` implementation; optional R applies to exact-artifact expansions, not to the retained bibliographic B2 route.

```text
B_final = B_core
          OR (P AND G1)
          OR (P AND G2)
          OR (P AND C1)
          OR (P AND M_B2 AND T2)   [only candidate-generating where not structurally contained]
```

All accepted partitions must be rerun after authorization from clean artifacts. Pilot IDs and counts remain outside the candidate corpus and evidence base.
