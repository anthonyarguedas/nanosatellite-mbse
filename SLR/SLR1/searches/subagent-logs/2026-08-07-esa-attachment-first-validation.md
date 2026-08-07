# ESA Indico attachment-first matcher validation

**Status:** completed `pilot_not_candidate_search` dry run with explicitly reconciled coverage failures. No contribution, material, attachment, or matcher hit was screened, retained as a candidate, or used as evidence. The valid post-authorization harvest must rerun from the root.

- **Run:** 2026-08-07 11:05:23–12:11:29 EDT (15:05:23–16:11:29 UTC)
- **Source:** complete public ESA Indico root plus every in-window event export
- **Date window:** 2011-01-01 through 2026-08-07 inclusive
- **Private pilot directory:** `.searches/eps-mbse-slr-2026/press-fix-pilots/2026-08-07/esa-dry-run/`
- **Active retained-artifact manifest:** 6,090 files, SHA-256 `ae1aba9681d63237ae33b0896cefb94787c24bc4086aeb40d8fe501ecde3f8e8`; every retained file was re-hashed successfully after the complete census and corrected no-network rematch

## Frozen implementation

| Artifact | SHA-256 |
|---|---|
| [`search-concept-dictionary.json`](../search-concept-dictionary.json), version `1.1.0-press-2026-08-07` | `1b2416c22840bd780d9b47f3ff81c6fd6466f13d52ee9d2ca7b429161a4232ab` |
| [`concept_matcher.py`](../tools/concept_matcher.py) | `895d7e8fb333d1ce684cda02e6ca795f6fbc29ee70a16cc894c5d8eaaa0203eb` |
| [`esa_indico_harvest_match.py`](../tools/esa_indico_harvest_match.py) | `78ff39c67371b4948bbae14b9cdbdf2b9b92f54bcd67858a8c35b5ef41e04d2b` |
| [`esa_indico_rematch.py`](../tools/esa_indico_rematch.py) | `ff2d71659089b18c935c636c6ce09bd3b5ae5c6887c247b2dc864e01ff1ada39` |
| [`esa-matcher-regression.json`](../fixtures/esa-matcher-regression.json) | `75520b52ba743b001ecf90b8350291c447a45ef1614d50983c176ccb0e82ef02` |
| [`esa-matcher-regression-results.json`](../fixtures/esa-matcher-regression-results.json) | `9ae0a8c6d92e7f2ae32ead7afae1940a993cb88911e85978b14cdd47cfe74c9d` |

All 10 positive/negative, field-level synthetic fixtures passed before the census. They cover attachment-only retrieval, cross-field joined metadata, Unicode-dash/hyphen-space normalization, spaced plurals, crossed US/UK modeling variants, object-oriented systems models, explicit battery/mode forms, generic SmallSat exclusion, explicit wildcard bounds, and standalone EPS/MBSE/MIL/SIL/PIL/HIL boundaries.

The matcher uses Unicode NFKC, entity decoding/HTML stripping, Unicode case-folding, Unicode-dash and ASCII-hyphen-to-space normalization, collapsed whitespace, complete bounded phrase/token matching, and no implicit wildcard, stemming, or lemmatization. The dictionary materializes every P/E/M form and the optional O/V tags. Exact searched fields and the no-cross-route-cooccurrence rule are encoded in the dictionary.

Runtime provenance: CPython 3.13.5; `requests` 2.34.2; `pdftotext` 26.04.0; macOS `textutil` for supported legacy office/RTF files.

## Whole-instance and contribution reconciliation

| Measure | Result |
|---|---:|
| Root events returned / unique | 437 / 437 |
| Root IDs equal top-level category 5∪6∪7 | yes |
| Category 9 IDs subset of category 6 | yes |
| Missing/unparseable root event dates | 0 |
| In-window events | 408 |
| In-window contribution exports attempted/retrieved/failed | 408 / 408 / 0 |
| Contributions parsed | 8,394 |
| Known coverage event IDs 161/329/386/407/472 | all present |

Every event export was obtained before matching. The event response shape was validated as one event object with its contribution array; top-level `count` was not misused as a contribution count.

## Attachment-first census and coverage

The harvester inventoried both current `folders[].attachments` and legacy `material[].resources` **before any P/M gate**, preserved every event/contribution association, deduplicated retrieval by public URL, and attempted every document-like URL irrespective of metadata.

| Measure | Result |
|---|---:|
| Material associations inventoried | 6,770 |
| Unique document-like URLs | 5,690 |
| Retrieved | 5,686 |
| Inaccessible/failed | 4 |
| Extractable normalized text parsed | 5,664 |
| Retrieved but unparseable/no extractable text | 22 |

The four retrieval failures were three HTTP 404 resources and one interrupted chunked transfer; all URLs/statuses remain in the private coverage artifact. Of the 22 parse failures, two were `pdftotext` failures and twenty yielded no normalized extractable text. These are coverage failures, not zero matches. Non-document images/audio/video remained in the inventory even though no text extractor applied.

To minimize storage and copyrighted-material retention after extraction, downloaded pilot binaries were deleted. `attachment-coverage.json` retains per-URL retrieval status, bytes, SHA-256, extractor outcome, and derived-text checksum; category/event JSON and all normalized extracted text remain private. The post-purge coverage SHA-256 is `acf977f7c569b5dc18920cd49db61018e5355635e9121cb1ab1c186f94a8f740`; the retention note SHA-256 is `219ace04185cc18287a2a5824092cfcb2d580be1344be114d3a4eb18cfe31f97`. A historical pre-purge manifest checksum (`aa03c79fa341f15a26c6167aa13d6dda2c3410416cbe1250583d1dbfd89c01b6`) is retained only as pilot provenance, not as a claim that those binaries remain available.

## Route and A/B reconciliation

Joined metadata and each individual attachment text were matched independently; no candidate was created by combining P from one route with M from another.

| Measure | Count |
|---|---:|
| Matched contribution/event-material subjects | 8,584 |
| Joined-metadata Stream B | 17 |
| Attachment-text Stream B | 62 |
| Both metadata and attachment routes | 5 |
| Metadata-only Stream B | 12 |
| **Attachment-only Stream B** | **57** |
| Stream B union | 74 |
| Stream A EPS-explicit tag / A∩B | 23 / 23 |
| B-only | 51 |
| A-only structural error | 0 |

Thus `A ⊆ B` held, and A is reported only as an EPS-explicit tag. The 57 attachment-only subjects empirically demonstrate why metadata-gated material retrieval was unsafe. These are aggregate matcher diagnostics only—not screening, candidate, precision, recall, or inclusion counts.

The first network run exposed an implementation over-attribution: event-level attachment text had been matched once as an event-material subject **and** inherited by every contribution at that event. No record was screened or used. The prospective harvester was corrected so event-level attachment text is matched only as an event-material subject, while its metadata may remain in the contribution's joined event context. A zero-network rematch then reused all 5,664 extracted texts and 408 saved event exports under the corrected association rule; the corrected aggregate above comes from that rematch (SHA-256 `8d54a4e17f6e2c8e2922ef8a4beae29f87838c664e4e581a55036ba2ea7173b4`). The superseded inflated route counts are not strategy results.

## Disposition

MAJOR-05's missing dictionary, unfrozen fields/normalization, absent regression fixtures, and metadata-gated attachment route are resolved in the prospective implementation. A final authorized run must repeat the complete census, record all current coverage failures, preserve metadata-versus-attachment routes and A/B overlap, and must not reuse this pilot union.
