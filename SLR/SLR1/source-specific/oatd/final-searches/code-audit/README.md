# OATD code audit

Date: 2026-09-05 UTC

## Findings

The earlier terminal failure assessment is superseded. Independent native UI submissions reached exact query readback and source totals. An adapter HTTP error did not establish that the entire search endpoint was unavailable.

The audit found four concrete problems in the previous final workflow:

1. It took one initial ID pass per gate. The source instructions require two before hydration and a confirming pass afterward.
2. It called every nonempty Record Details abstract full. OATD truncates some abstracts near 3,072 characters. The hidden result-card abstract can contain the same truncated text.
3. It discarded native Degree and Degree Level fields. Its constant publication type describes the ETD index scope.
4. It looked for `Department/Discipline`. The observed detail label was `Discipline/Department`.

The first corrective implementation preserved `form=basic`. Run 008 reached four gates and then failed on the tailoring gate. Subsequent diagnostics showed that the exact tailoring, model, and structure queries could succeed through independent native submissions. Several intermediate driver checks still failed. Their evidence remains separate from final records.

The revised driver follows the successful native UI sequence. It observes the rendered page, fills the complete controlled query once, submits the real basic form, observes the result, and applies the existing exact-readback and completeness checks. It uses a directly created owned page for each gate pass in the same shared Chrome profile. The backend cause of the HTTP 500 responses remains unknown.

## Live evidence

- `native-ui/`: an independent one-literal search returned 1,340 matches.
- `controlled-route-comparison/`: the English and 2011 through 2026 controls returned 682 matches through both compared transports.
- `adapter-smoke/`: the first exact gate returned a rendered HTTP 500 through the earlier adapter route.
- `exact-gate-native/`: native submission of that exact controlled gate returned 17 matches.
- `native-transport-smoke/`: adapter parsing validated 17 cards and one detail. The MIT abstract cell contained 3,072 characters and an ellipsis. Degree and Degree Level were visible.
- `card-abstract-inspection/`: the result card contained the same truncated MIT abstract. This diagnostic contributes no detail record.
- `tailoring-gate-native/` and `model-gate-native/`: exact controlled native submissions returned explicit zeros.
- `structure-gate-native/`: the exact controlled structure gate returned three matches.
- `native-rendered-observation-smoke/`: the revised driver validated the three-record structure gate and the singleton central-asset gate. Both owned pages closed.

Diagnostic result prefixes and historical pilot records contribute no final discovery records.

## Full abstracts

`repository-feasibility/` retains fresh repository evidence for full abstracts. These are metadata enrichment inputs, with no additional discovery count.

- MIT, Colorado State University, and Cornell expose complete abstracts in repository metadata.
- The public Figshare item API exposes Wollongong's complete description and native thesis type.
- Kyutech exposes the full Abstract and the native resource type `doctoral thesis`. OATD prepends a degree note and table of contents to this record's abstract. Enrichment preserves that original description and verifies the actual abstract prefix separately.
- Keio's metadata abstract is empty. PDF page 3 contains the complete abstract. Page 2 identifies the work as a master's dissertation. Only abstract and type metadata are extracted from this document. No screening decision is assigned.

The enrichment join requires the same normalized title and the entire available OATD abstract prefix when present. It retains original OATD text, source locations, retrieval times, and file and text hashes. It fails if any incomplete final record lacks verified full text for its abstract.

## Offline checks

Five focused tests passed:

```text
uv run --with playwright -m unittest discover -s SLR/SLR1/source-specific/oatd/scripts/oatd_final -p 'test_run.py' -v
uv run --with playwright -m unittest discover -s SLR/SLR1/source-specific/oatd/scripts/oatd_final -p 'test_enrich_abstracts.py' -v
```

They cover unchanged query semantics, native form parameters, checkpoint metadata, honest source truncation flags, three-pass gate publication, terminal union verification, and full-abstract enrichment without changing IDs or creating another discovery event. Historical records are used only as offline fixtures in temporary directories.

## Final execution

The successful final publication is in [`../corrective-013/`](../corrective-013/). It completed at 2026-09-05 06:31:21 UTC. Its validation report confirms 24 required membership passes, 27 hydrated source records, and 35 gate occurrences. The full-abstract sidecar and its separate validation confirm 27 complete abstracts and 27 source publication types.

The 16 initial final passes from `corrective-009` remained valid. Later continuations retained completed detail checkpoints. No initial pass or completed detail was silently treated as a new observation. The final plan binds those files by hash. All eight post-hydration confirming sets matched both initial sets.

Detail investigation exposed further local timing problems. A load-state check could inspect the old document before link navigation. An explicit detail-navigation wait and bounded polling through transient execution-context changes resolved that race. Cached browser Back required the adapter's commit-based restoration and source-state checks. Waiting for a new DOMContentLoaded event incorrectly timed out on a restored page.

A full-query MIT detail route failed while the same observed Record ID with empty `q` returned identical bibliographic fields and abstract text. An empty-`q` lookup failed for another record that the awaited native link retrieved. The final plan therefore permits one alternate display-context lookup after HTTP 500 or 504 and a 120-second pause. Exact ID and title readback are mandatory in both modes. The successful continuation completed its 17 remaining details without needing that fallback.

The final source records contain 18 complete displayed OATD abstracts, eight truncated abstracts, and one absent abstract. The nine verified repository replacements supply the full-abstract sidecar. Native degree levels are present for 21 records. Missing levels remain explicit. Source publication types describe ETD scope and do not assign reviewer eligibility codes.

The common cutoff remains 2026-08-24. Two cutoff-year records require exact date screening. The final source and enrichment validators both passed. Earlier failures remain historical evidence and create no additional discovery counts.
