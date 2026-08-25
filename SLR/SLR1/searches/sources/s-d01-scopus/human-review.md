# Scopus source-method human review

- **Task:** `S-D01`
- **Recorded:** 2026-08-23T14:02:36-04:00
- **Reviewer:** review owner
- **Protocol commit reviewed:** `38ab61287443693ddabdd4bb855d535a4585ae35`
- **Approved adapter implementation:** `anthonyarguedas/agent-tools` commit `9aef2155f0073a8b82f7d5af3ec0870f6e6aeef2`
- **Approval provenance:** the Git commit containing this source packet is the approval record; no separate approval hash ledger is maintained.
- **Decision scope:** diagnostic source-method results only; this is not a final search, screening decision, or authorization of `R-002`.

## Approved decisions

The reviewer approved H1–H5:

1. **H1 — Source-native translation:** approve the nine Scopus partitions and 12 source-native cells, including the lossless four-cell BT2 implementation.
2. **H2 — Proximity fallback:** approve `W/6` as a lossless Scopus implementation that may be one intervening token broader than the cross-source rule. Do not report it as exact equivalence.
3. **H3 — Indexed terms:** approve mandatory free text with no `INDEXTERMS` supplement because no usable Scopus-wide hierarchy, scope-note, narrower-term, or explosion route was established.
4. **H4 — Capture and completeness:** approve rendered adapter capture rather than native export. A final nonzero cell requires fixed controls, native abstracts, two complete ordered stable-identity passes, and total/page/identity reconciliation; any mismatch fails with `total=null` and no imported prefix.
5. **H5 — Adapter behavior:** approve the bounded readiness and display-cap corrections implemented in adapter commit `9aef2155f0073a8b82f7d5af3ec0870f6e6aeef2`. A rendered cap must produce `ScopusDisplayCapError`, `total=null`, and no retained prefix.

Supporting evidence is indexed in pilots P08–P10 and summarized in [`guideline.md`](guideline.md).

## Evidence-cutoff sequencing decision

`P-001` is not a prerequisite for a source pilot or for approval of a reusable source method. The protocol already requires the common evidence cutoff only before the first final search. When a pilot needs an upper date bound to test controls, use the pilot execution date as a clearly labelled diagnostic bound; it does not become the review's common cutoff and pilot records remain ineligible for import.

The review owner will choose the common evidence cutoff after the source pilots and before any final search. The final Scopus implementation must then apply that one fixed cutoff or the protocol-specified local handling.

## Remaining gate

The Scopus method is human-approved on H1–H5 but is not yet formally accepted in Part 2. The adapter is pinned by commit and this approval is recorded by the Git commit containing this source packet. Complete `S-C01`, apply any terminology decision to the protocol, dictionary, and translations, and then perform the formal `S-D01` status reconciliation. `P-001` remains a final-search dependency, not a pilot-acceptance dependency.

## Post-review diagnostic status

The Scopus portion of `S-C01` was completed after this H1–H5 decision under pilots [`P13`](pilots/S-D01-P13-20260823T145616-0400/) and [`P14`](pilots/S-D01-P14-20260823T150131-0400/). It carries two candidate families forward for cross-source review but makes no normative change. This note does not extend the earlier human approval to the new term-use judgments: the review owner still needs to review them with the Web of Science, IEEE Xplore, and Compendex/Inspec results before the protocol, dictionary, translations, or formal `S-D01` status can change.
