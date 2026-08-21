# S-D09 OATD diagnostic observations

- **Pilot ID:** `S-D09-P01-20260821T043952+0000`
- **Task/source:** `S-D09` / Open Access Theses and Dissertations (OATD)
- **Protocol commit:** `ad77460df82764312fb701f6be4ebf7eb5051c41`
- **Status/recommendation:** **blocked** / **skip_for_now**
- **Scope guard:** diagnostic only; `screening_performed=false`; `candidate_import_permitted=false`.
- **Claim labels:** **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**. Only the first two can support a reusable guideline.

## Stop condition and access disposition

- **[observed]** A normal local-CDP browser loaded OATD's public home page and exposed basic and advanced forms. No query was submitted, no record/detail page was opened, and no login, credential, cookie inspection, or challenge interaction occurred. See `E-01` in [`evidence-index.json`](evidence-index.json).
- **[observed]** A direct HTTP retrieval of the public FAQ URL `https://oatd.org/faq.html` returned HTTP 403 with `Cf-Mitigated: challenge`, Cloudflare server headers, and a “Just a moment” response. The saved diagnostics were read before this observation was recorded. See `E-02`.
- **[observed]** The challenge ended all source requests. There was no retry loop, browser workaround, hidden/private endpoint, credential entry, CAPTCHA interaction, query-cell submission, result retrieval, screening, candidate activity, full-text download, or final-event write.
- **[inferred]** This is an access/challenge failure rather than a source zero. Every query-cell total is therefore `null`, not zero.

## Safe current visible-interface inventory

| Area | Observation | Status / basis |
|---|---|---|
| Public source identity | Rendered title identifies OATD / Open Access Theses and Dissertations. | **[observed]** E-01 |
| Basic route | Visible GET form action `/oatd/search`, `q` search input, hidden `form=basic`, Search submit. | **[observed]** E-01 |
| Advanced route | Visible GET form action `/oatd/search-composer`, hidden `form=advanced`. | **[observed]** E-01 |
| Advanced rows | Four visible `joiner`/`box`/`field` rows and three visible And/Or inter-row controls. | **[observed]** E-01 |
| Advanced fields | Visible choices: any field, title, author name, abstract, university/publisher, subjects/keywords, department/discipline. | **[observed]** E-01 |
| Other advanced controls | Visible language, country, earliest, latest, sort, Creative Commons, and 30/60/100 page-size controls. | **[observed]** E-01 |
| Indexed-resource boundary | Homepage copy advertises theses/dissertations and more than 1,100 institutions, but this does not prove actual participating-repository coverage or current index completeness. | **[observed]** copy / **[untested]** boundary proof, E-01 |
| Basic/advanced query grammar and current scope | No query was submitted after the challenge stop. | **[untested]** |

The homepage's visible `7,464,811` link is retained only as non-query copy in E-01. It is **not** treated as a review-query source total, a resource-boundary proof, or a completeness result.

## Required diagnostic matrix

| Check | Result | Basis | Evidence / consequence |
|---|---|---|---|
| Current public basic and advanced visible controls/routes | verified only as visible UI inventory | **observed** | E-01; no semantic control claim |
| Phrase/quote, AND/OR/NOT/precedence, parentheses | untested | **untested** | No query submitted |
| Punctuation/hyphens, case/acronyms | untested | **untested** | No query submitted |
| Stemming, lemmatization, automatic expansion, wildcard | untested | **untested** | No query submitted; no wildcard candidate used |
| Query length, GET transport, exact echo/rewrite | untested | **untested** | Form GET observed; candidate transport not executed |
| All 11 exact source translations | blocked before source submission | **untested** | E-03 local structure only; all source totals `null` |
| Date lower bound and exact-day behavior | untested | **untested** | Earliest/latest visible only; P-001 upper cutoff unset |
| Language controls | untested | **untested** | English visible only; no native limit applied |
| No unapproved limits | no query submitted | **observed** | No access/CC/content/type/country/repository limit applied |
| Result total/range/page size/pagination/export | untested | **untested** | No result page opened |
| Record Details / OATD Record ID / repository-resource provenance | untested | **untested** | No result/detail page opened |
| Duplicate behavior and two-pass completeness | untested | **untested** | No result set exists |
| Native explicit zero | untested | **untested** | Challenge is `null`, never zero |
| Access/challenge failure handling | verified | **observed** | E-02; stopped cleanly, no workaround |

## Partition/cell receipt

The files below are exact local UTF-8 candidates, each with one terminal LF. `E-03` confirms local term coverage, hashes, encoding, balanced parentheses, no wildcard, and no prohibited SmallSat term. It **does not** establish OATD query acceptance or lossless source-native semantics.

| Partition | Cell | Query bytes/chars | SHA-256 | Source submission | Source total | Retrieved diagnostic count |
|---|---|---:|---|---|---:|---:|
| A1 | A1-C1 | 603 | `a7f819539645e721389e2820a2ac845620b9859b286a45ab8e4805d348c2f82e` | not sent; blocked | null | 0 |
| A2 | A2-C1 | 880 | `d091992a3db20b9c5be2a742d5b85fc9780300a495493af2dd5a98afd03157a1` | not sent; blocked | null | 0 |
| A3 | A3-C1 | 593 | `0fd37daa848499cecaac5a3ebcb330f162295531d13130e6fa73faf0dc99044b` | not sent; blocked | null | 0 |
| B1 | B1-C1 | 385 | `03b94a4ff00aeea7649756a4175769dceac94d1bb238677423a8b948f39dbaec` | not sent; blocked | null | 0 |
| B2 | B2-C1 | 621 | `9ca89a0178babd7f791efdcfca255def1282d7d3d0bd51ae0471921031e0e285` | not sent; blocked | null | 0 |
| BG1 | BG1-C1 | 462 | `fe14a86535c5ce3cbccc3f1718ef519924f60a89e789eeda2298b709f7065f9e` | not sent; blocked | null | 0 |
| BG2 | BG2-C1 | 385 | `f5abfa7ef97662e2dd00ae8fbf992f974c194e39d77710110949514e3e7b9e52` | not sent; blocked | null | 0 |
| BC1 | BC1-C1 | 916 | `0fb2b484e8ab95bfe249c92caf498411196f3a4cdc27ffb2bb24d4acfb62ef10` | not sent; blocked | null | 0 |
| BT2 | BT2-C1 | 1,257 | `c0c4748462cbaf27d3e06f30bf3a3819b821aa29e563cc8c59fc943c9f2077e4` | not sent; blocked | null | 0 |
| V1 | V1-C1 | 823 | `5bfd4227edebb240aa17b15fc682cb763c7d561fd2facf95998ea11399950a2e` | not sent; blocked | null | 0 |
| O1 | O1-C1 | 846 | `df9527778cfec382163219053b4e016be8840464bfa1d6e678e1e629dea1e0ac` | not sent; blocked | null | 0 |

**Coverage check — [observed] local only:** all 11 scheduled partitions appear once; `A1/A2/A3` map to Stream A, `B1/B2` to core B, `BG1/BG2/BC1/BT2` to expanded B, and `V1/O1` to sensitivity. The local check found no omitted finite term in its designated blocks. No union is claimed from counts, and no source stable ID was observed.

## Boundary, record, and provenance guard

- **[official_documentation]** The review protocol/crosswalk requires OATD's own source total and PRISMA `other_methods` accounting. It also requires degree completion, full-report language, resource accessibility, and eligibility to be determined later rather than inferred from OATD metadata. See E-04.
- **[untested]** Current OATD index-record fields, Record ID stability, repository identity, university/publisher provenance, resource URL behavior, linked-content accessibility, and current indexed-resource boundary.
- **[inferred]** A future pilot must prove an OATD Record ID through the normal Record Details page and retain repository/resource URLs as separate fields. It must never promote any of those fields into completion, degree type, language, access, or eligibility decisions during a source pilot.

## Controls and future procedure (not executed)

- **[official_documentation]** The lower date is 2011-01-01. The common upper cutoff remains unset under P-001. See E-04.
- **[observed]** The advanced form visibly exposes earliest/latest, language, country, `cc_only`, sort, and page-size controls. No behavior was tested.
- **[inferred]** At re-pilot, use no language/access/Creative-Commons/content/peer-review/publication-type/country/institution/repository limit. Validate date and language independently; only after P-001 may an exact upper date be tested.
- **[inferred]** On a future challenge-free result set, require exact echo, source total/range, stable OATD Record IDs, contiguous pagination, no within-event duplicate/missing IDs, and two complete comparable passes. Any failure sets `total=null` and imports nothing.

## Evidence index and retention

| ID | Classification | Safe evidence and retention |
|---|---|---|
| E-01 | observed | Ignored `SLR/SLR1/searches/worklogs/s-d09-oatd/S-D09-P01-20260821T043952+0000/derived/home-rendered-ui-summary.json`; parsed safe DOM summary, SHA-256 `7c2e4db44d3683274d44bec7c30e757256d7d6ca2d6578c3fab3756a5c25bb49`, `metadata_only`. |
| E-02 | observed | Ignored `.../official/faq-diagnostics/response.json`, SHA-256 `6e8d87c9e4d8ffa18cb358289a13717446f42ec6f8d473aade1a570555c8e68b`, plus ignored raw/decoded Cloudflare body, SHA-256 `16d4b17f7bbe49e4e93628bc052c8852a8d48276d6d4aaf210bfc3570fc1828a`; `restricted`. No challenge token or final challenge URL is copied into tracked files. |
| E-03 | observed | [`translation-integrity.json`](translation-integrity.json); tracked local structural evidence only. |
| E-04 | official_documentation | Review protocol/crosswalk: `SLR/SLR1/protocol-discovery-and-appraisal.md`, `SLR/SLR1/searches/source-interface-prisma-crosswalk.json`, and the Part 1 rules needed for cutoff/definitions. |

The complete machine-readable index, including artifact checksums and access classes, is [`evidence-index.json`](evidence-index.json). No raw source result, abstract, full text, credential, cookie, session URL, or search URL is tracked.

## Protocol impact and smallest human follow-up

- **[observed]** `semantic_change:false`; no protocol, dictionary, crosswalk, schema, template, task, log, or final-event file changed.
- **[inferred]** Smallest follow-up: once the Cloudflare condition is absent, make one normal public rendered-browser preflight in a new owned tab. Stop again on any challenge; otherwise validate basic and advanced grammar/echo plus a controlled zero, singleton, positive, date, identity, and pagination diagnostic before using any candidate file.
- **[untested]** No current interface behavior beyond visible controls is accepted from this pilot.
