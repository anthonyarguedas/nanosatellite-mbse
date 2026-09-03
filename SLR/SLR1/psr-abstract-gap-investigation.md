# PSR abstract gap investigation

## Conclusion

The missing full abstracts originate before deduplication and merging.

| Source | Classification | Finding |
|---|---|---|
| Scopus | Source-specific execution gap | The final discovery runner explicitly used `--skip-full-abstracts`. The final assessment records abstract recovery as `pending`. |
| Web of Science Core Collection | Source-specific adapter and validation gap | The adapter accepted the native RIS default `Author, Title, Source`. That export contains no `AB` or `N2` fields. The adapter did not select or verify a full-record export option. |
| Shared merger | Working as designed for metadata | It preserves a nonempty `abstract` and chooses richer values when duplicates are merged. |
| Project candidate builder field mapping | Working as designed for metadata | It preserves a source abstract and all available Web of Science snippets. |
| Project candidate readiness gate | Validation gap | It allowed candidate generation while Scopus recovery was `pending` and Web of Science abstract coverage was unchecked. |

## Stage counts

The eight final source artifacts contain 470 source-record occurrences.

| Stage | Records | Full abstracts | Abstract snippets |
|---|---:|---:|---:|
| Final source artifacts | 470 occurrences | 0 | 110 Web of Science occurrences |
| Shared merger | 419 records under its original identity keys | 0 | 103 |
| Corrected project deduplication | 343 reports | 0 | 103 |

All 103 unique Web of Science records retain their snippets after merging. The corrected candidate set has 240 reports with neither a full abstract nor a snippet.

## Scopus trace

The Scopus final plan sets `full_abstracts` to `false` and `skip_full_abstracts` to `true`. The final runner passes `--skip-full-abstracts` to the adapter and validates blank abstracts with `abstract_source` equal to `not_rendered`. The source assessment states that a canonical EID-only recovery is required and gives its status as `pending`.

The blank values do not establish that Scopus lacks the abstracts. The adapter labels every skipped row `abstract_not_available: true`, while also recording `abstract_source: not_rendered`. Historical pilot-only EID follow-up artifacts recovered full abstracts, which confirms that at least some of these source records have native abstracts. Those pilot artifacts are diagnostic and are not final enrichment evidence.

This is an incomplete source-specific workflow. The successful final discovery run was intentionally limited to identifiers and bibliographic metadata. It was not an abstract-retrieval attempt.

## Web of Science trace

Every final Web of Science JSON row has an empty `abstract` and a nonempty rendered snippet. Every native RIS sidecar lacks `AB` and `N2` tags.

The adapter can parse `AB` and `N2` into `abstract` when those tags exist. Its export control records `native_record_content_default` as `Author, Title, Source`. The export routine verifies the record range and RIS format, but it does not select or verify a full-record content option. The final source assessment verifies identifiers, counts, screenshots, and RIS reconciliation without checking abstract coverage.

The snippets prove that abstract text exists on the Web of Science result surface for all 103 unique records. The adapter captured only the shortened result-card text.

## Merge trace

The shared merger reads `raw["abstract"]` and `raw["snippet"]`. Its richer-value selection retains nonempty text when duplicate records are combined. The project candidate builder follows the same rule. A check using a retained 1,303-character Scopus pilot abstract preserved all 1,303 characters through candidate construction and through a two-source merge.

The earlier DOI-first identity defect caused duplicate candidates. It did not remove abstracts. Both source inputs already had empty full-abstract fields.

## Readiness trace

`deduplication.py` accepted each source when its final search assessment passed and its discovery partitions were complete. It did not require completed abstract recovery. The Scopus assessment therefore passed as a discovery assessment while separately reporting abstract recovery as `pending`. The Web of Science assessment had no abstract coverage condition. This validation gap allowed a structurally valid candidate file to be released before its title-and-abstract metadata was ready.

## Required repair

1. Run final Scopus EID-bound abstract recovery against the accepted 327-ID final ledger. Preserve unresolved records as unresolved.
2. Add a Web of Science follow-up route that explicitly selects and verifies full-record content, or hydrate each accepted WOS accession from its full-record page.
3. Save source-specific enrichment artifacts instead of rewriting the final discovery artifacts.
4. Make the source assessments report abstract recovery coverage and unresolved counts.
5. Make candidate creation require an explicit abstract-recovery disposition from each source.
6. Rebuild `psr-candidates.json` from the final discovery artifacts plus validated enrichment artifacts while transferring screening decisions by source record ID.

Blank abstract fields must remain classified as not collected until a source-specific follow-up proves that an abstract is unavailable.

## Resolution

The corrective Scopus run retained the same 327 source IDs and recovered 134 abstracts during direct searches. It exposed a stale cross-page abstract control that had left later-page abstracts blank. The adapter now fails closed on that state. Four canonical one-page EID follow-ups recovered the remaining 193. The corrective Web of Science run retained the same 103 source IDs and recovered all 103 abstracts through abstract-inclusive RIS. Both corrective assessments passed.

The rebuilt candidate set contains 343 deduplicated reports. Every report now has a full abstract. All prior screening decisions remain linked to the same 430 source record IDs. The source adapter repairs are committed in `~/agent-tools` as `a6bb3f7`.
