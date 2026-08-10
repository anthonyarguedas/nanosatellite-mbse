# ESA Indico and NTRS reusable-artifact pilots

**Date:** 2026-08-10
**Classification:** `pilot_not_candidate_search`
**Assessment:** model-assisted; not a human information specialist; no screening

These pilots tested finite query/matcher coverage and aggregate opaque-set behavior only. No title, abstract, bibliographic metadata content, full text, relevance, eligibility, artifact evidence, or RQ1-G grade was inspected. Pilot subjects/IDs are not candidates and cannot be reused in final discovery.

## ESA Indico deterministic route matcher

Version 1.3 expands the attachment-first matcher without changing the complete-census requirement:

- core B remains `P AND M`;
- expansion B is `P AND` a complete G1/G2 or conservative C1 artifact, relation-free;
- all required components must occur within the joined-metadata route or within one individual attachment route;
- P/G/C/R/T terms cannot be assembled across metadata and attachment routes or across separate attachments;
- an R occurrence qualifies only as an independent optional tag when its span does not overlap the active artifact's required component span;
- T2 is a local core-B tag because ESA core is already `P AND M` without the bibliographic B2 relation gate; and
- E-explicit expansion records are retained as separate tags and are not relabelled Stream A.

Regression results were 19/19 [concept fixtures](../fixtures/esa-matcher-regression-results.json) and 13/13 [route/attachment fixtures](../fixtures/esa-genericity-route-regression-results.json). They include positives for G1/G2/C1 and all-of artifacts plus negatives for architecture self-satisfaction, incomplete variation-point/domain-language artifacts, cross-route co-occurrence, and cross-attachment co-occurrence.

A no-network rematch reused the preserved complete 2026-08-07 census strictly as a method diagnostic (`network_requests=0`): 8,584 subjects and 5,664 previously extracted attachment texts. Aggregate results were core B 74; G 32; C1 15; G∩C1 6; complete relation-free expansion 41; core∩G 18; core∩C1 14; core∩expansion 26; core-only 48; expansion-only 15 (14 G-only versus core/C1 and 1 C1-only versus core/G); total B 89; unchanged A 23; structural A-only 0; E-explicit G/C1 15/5 (union 16); independent-R tag 41; and T2 tag 55. Total-B metadata/attachment routes were 20/75 with overlap 6; G routes were 3/30 with overlap 1, and C1 routes were 6/9 with no overlap. The clean final search must harvest the whole current instance and attachment inventory anew.

## NTRS finite matrix

The source contract remains one population atom plus one complete model/artifact atom, separated by spaces; quoted phrases only; no Boolean operators, parentheses, fields, or wildcards. Every cell uses the date body, 100-record zero-based pagination, stable-total/unique-ID/full-retrieval reconciliation, and its own log entry.

| Partition | Design | Cells completed | Pilot aggregate |
|---|---:|---:|---|
| Core B | `10 P × 18 M` | 180/180 represented across pilots | seven-form simple sum 39/union 6; added 54 cells all zero |
| Precise G | `10 P × 25 G` | 250/250 represented across pilots | seven-form simple sum/union 1, core∩G 1/G-only 0; added 75 cells all zero |
| Conservative C1 | `10 P × 23 C1` | 230/230 represented across pilots | all seven-form and added 69 cells were valid zeros |
| **Total final design** | core + G + C1 | **660/660 represented across pilots** | pilot overlap/zeros cannot remove a final cell |

The initial reconstruction exposed that the version-1.2 text said six P terms/108 cells while listing seven terms. A focused exact `"cube sat"` follow-up completed the 18 M + 25 G missing cells (43/43), all valid zeros, thereby completing the 301-cell seven-form core/G diagnostic. C1 then completed 161/161 separately. A final vocabulary audit found three source-representable forms still compressed without source-semantic equivalence: `nanosatellites`, `"nano satellite"`, and `"nano-satellites"`; a focused 3×(18+25+23)=198-cell pilot reconciled 198/198 with valid zeros and no failure. NTRS can change retrospectively, and neither zero yield nor opaque overlap establishes structural equivalence, so all 660 cells remain mandatory in a clean final directory. E and T2 are deterministic local tags over the full deduplicated returned metadata; they cannot add records.

## Integrity and limits

The tracked dictionary, matcher, harvester/rematcher, and fixtures are the authoritative final specification. Private pilot artifacts are owner-restricted under the ignored amendment-pilot tree. NTRS copy-manifest SHA-256 values are `d539931a34f69a8ac93ff51ff7954aeef4acfe189df5a3d77fa3f34b3fbf21aa` (seventh-term follow-up), `40373c3d7463ebe0b644a08581655a3a7666855840304c10722d860f5fa8da80` (seven-form C1), and `6a716358cdf573187540adcf580220be0ed773a7718fd7c8c301ec193b927844` (three remaining population forms). The accepted relation-free rematch used dictionary `1402a145010632894a2a54f39ec1cdc87323331ab9eaadd236025ec30668ed75`, matcher `08f258393f35b6ae573f8e0a4cc0f9354af996b22d335b459065e9c62f30425a`, harvester `dd90c774ce3a5884144298c83194a71d03e1944c52acd1b9f13b6d5f5ee59525`, and rematcher `72a8bf32fe8e60511e9e0aea0cc32409ad954635d0609ab3a37fcb57baaec0f1`; its private manifest SHA-256 is `e2730cfd88ec35353bef4ad6d5ebfc698dc442c91da34e17009f667f9de2aac8`. After that run, only non-matching comments/provenance-policy wording and a dictionary scope label were clarified to distinguish local relation-free G/C1 from bibliographic B2 and separate R/T tags. Current dictionary/matcher/harvester/rematcher hashes are `b4a6b059256aa61c922b0998d8086f1727dfedfd4113ef883b244a4187f0e932`, `08f258393f35b6ae573f8e0a4cc0f9354af996b22d335b459065e9c62f30425a`, `a59500920c1560910424efeca3b4231a5d90c271dea0d4f73c5700a01ad0fa72`, and `93b74a1c91747ba36753e1ed8af51e1e9b182827cfe9ea85ba1206c40d5d3240`; matching semantics and 19/19 plus 13/13 outcomes are unchanged. No aggregate above is an identification, screening, eligibility, inclusion, or evidence count.
