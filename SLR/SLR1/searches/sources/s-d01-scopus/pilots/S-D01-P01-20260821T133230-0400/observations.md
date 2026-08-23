# S-D01 Scopus pilot observations

- **Pilot ID:** `S-D01-P01-20260821T133230-0400`
- **Status:** `partial` diagnostic pilot; not accepted and not report-ready.
- **Window:** 2026-08-21T13:32:30-04:00 to 2026-08-21T14:06:04-04:00.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** no screening, no candidate import, no full-text retrieval, and no final-event artifact.

Basis labels are used as follows: **[observed]** is a current rendered-UI observation; **[official_documentation]** is a current Scopus Support claim; **[inferred]** is a conservative conclusion from those materials; and **[untested]** is deliberately unresolved. Protocol instructions are identified separately and are not interface-behavior claims.

## 1. Access, source boundary, and current interface

- **[observed]** The normal Scopus home page loaded through the existing authorized local Chrome context and exposed an institutional-access indicator and user menu. No login, CAPTCHA, challenge, or credential prompt was encountered. The native Advanced Search route was `https://www.scopus.com/pages/search/publications?type=advanced`.
- **[observed]** The live page exposed Documents, Preprints, and Secondary documents results categories; this pilot did not apply a category, publication-type, access, venue, or source-subset restriction.
- **[observed]** The current `search_scopus.py` rendered-UI adapter failed on the initial count-only `TITLE-ABS-KEY("CubeSat")` probe with `ScopusRequestError`, `total=null`, and zero retained records. Its safe error artifact is restricted. The normal UI then successfully ran all later diagnostics in a separately owned tab.
- **[inferred]** The failure is a current adapter/interface mismatch or route-parsing issue, not evidence of unavailable Scopus access and not a zero.
- **[observed]** Advanced Search visibly exposed `TITLE-ABS-KEY`, `AUTHKEY`, `INDEXTERMS`, `LANGUAGE`, `PUBYEAR`, `PUBDATETXT`, `SRCTYPE`, `INDEX`, `EID`, and `DOI`. The source-native translation uses `TITLE-ABS-KEY` only for mandatory free text.

## 2. Direct partition syntax checks

All executions were count-only. Exact strings are outside Markdown under `queries/`; current count evidence and hashes are in [`count-ledger.json`](count-ledger.json).

| Cell(s) | Current source display | Basis and qualification |
|---|---:|---|
| A1 | 4 | **[observed]** native result range 1–4 of 4; no records retained. |
| A2 | 14 | **[observed]** native result range 1–10 of 14. |
| A3 | 6 | **[observed]** native result range 1–6 of 6. |
| B1 | 90 | **[observed]** native result range 1–10 of 90. |
| B2 | 98 | **[observed]** native result range 1–10 of 98. |
| BG1 | 6 | **[observed]** native result range 1–6 of 6. |
| BG2 | 10 | **[observed]** native result range 1–10 of 10. |
| BC1 | 24 | **[observed]** native result range 1–10 of 24. |
| BT2-01 / -02 / -03 / -04 | 2 / 3 / 0 / 4 | **[observed]** all four lossless cells parsed. BT2-03 showed the native no-documents message and is an explicit cell zero. The union total is **null** because cross-cell identities were not retrieved/deduplicated. |

- **[observed]** The original 7,949-character BT2 expression timed out in local DevTools `Input.insertText` before Search activation. It was never submitted to Scopus; `total=null`. The lossless four-cell union is therefore an implementation response to a local transport failure, not a claimed Scopus length limit.
- **[inferred]** [`translation-audit.json`](translation-audit.json) passed: every ordinary finite term is literal in its cell; BG1/BG2/BC1 pair cross-products are present; and BT2 covers all 56 × 4 required pair clauses. This is a file-algebra check, not a source semantic proof.

## 3. Search-language diagnostics

| Test | Displayed total(s) | Observation |
|---|---:|---|
| Loose hyphen phrase / loose space phrase / exact brace hyphen phrase | 61 / 61 / 47 | **[observed]** scoped phrase behavior differed for exact braces; no form was removed from the translation. |
| Unparenthesized / parenthesized precedence | 22 / 22 | **[observed]** this scoped pair agreed; all final strings still parenthesize every Boolean block. |
| `nanosat*` / four contiguous literal forms, each with `SysML` | 6 / 6 | **[observed]** scoped contiguous-form equality only. **[inferred]** it cannot prove separated/hyphenated equivalence, so no wildcard substitution is made. |
| `nano-satellite` / `nano satellite`, each with `SysML` | 1 / 1 | **[observed]** scoped count equality only; both forms remain. |
| `MBSE` / `MBSE*`, each with `CubeSat` | 53 / 53 | **[observed]** equality does not prove standalone-token behavior. |
| default `battery` / exact `{battery}`, each with CubeSat and SysML | 0 / 0 | **[observed]** both were native explicit zeros; this does not measure general lemmatization. |
| `"mission-agnostic" W/6 model` with CubeSat | 0 | **[observed]** syntax was accepted and produced an explicit zero. **[untested]** endpoint/intervening-token counting remains unresolved. |
| `PUBYEAR IS 2011` / `PUBYEAR AFT 2010 AND PUBYEAR BEF 2012` | 127 / 127 | **[observed]** both syntax forms were accepted for the diagnostic year; no final cutoff was selected. |
| `LANGUAGE(english)` / `SRCTYPE(p)` | 22 / 18 | **[observed]** field syntax was accepted only; neither is a justified final restriction. |
| `INDEXTERMS(SysML)` with CubeSat | 4 | **[observed]** the indexed-term field syntax was accepted. |

- **[official_documentation]** Scopus Support’s current Advanced Search article (updated 2024-08-15) says quotes are loose/approximate phrase search, braces are exact phrase search, and gives the current operator precedence and field-code behavior: <https://service.elsevier.com/app/answers/detail/a_id/11365/supporthub/scopus/#tips>.
- **[official_documentation]** Scopus Support’s current complex-search article (updated 2025-10-20) says non-exact English/scientific terms can be lemmatized, hyphens are punctuation outside exact phrases, `W/n` is within and `PRE/n` is preceding, and complex strings can be rejected/ambiguous despite no stated explicit query-length limit: <https://service.elsevier.com/app/answers/detail/a_id/15137/supporthub/scopus/>.
- **[inferred]** `W/6` is a conservative broader same-field retrieval expression for the protocol’s <=5-intervening-token pairs, but the exact distance convention has not been independently verified. This prevents guideline acceptance.

## 4. Indexed terms and controlled vocabulary

- **[observed]** A minimum diagnostic record showed an `Indexed keywords` section with separate engineering controlled-term, uncontrolled-term, and main-heading fields. The record content, identity, and terms are retained only in the ignored restricted capture.
- **[observed]** That visible section had no link, hierarchy browser, explosion control, selector, or expansion control.
- **[official_documentation]** The current Advanced Search help describes `INDEXTERMS` as an indexing-term field, but the inspected material did not establish a scope note, hierarchy, narrower-term set, or explosion behavior for Scopus as a whole.
- **[inferred]** No controlled descriptor is proposed. Free-text remains mandatory; the current evidence does not support calling generic Scopus indexed keywords a thesaurus or allowing a generic systems-engineering heading to satisfy `M_H` alone.

## 5. Date, language, pagination, identity, export, and caps

- **[observed]** Results defaulted to Date (newest); visible alternatives included Date (oldest), citation, relevance, first-author, and source-title orderings. Visible page sizes were 10, 20, 50, 100, and 200.
- **[observed]** A2 moved from 1–10 of 14 to 11–14 of 14 through the current native Next control under the default order and 10/page.
- **[observed]** A four-record A1 set had identical ordered canonical publication-path sequences, source-displayed totals, and visible-row counts across two complete native UI passes. [`identity-receipt.json`](identity-receipt.json) retains only hashes/counts; raw paths are restricted.
- **[untested]** This small A1 proof does not validate complete retrieval for all cells, a multi-page full event, BT2 cross-cell deduplication, EID/DOI export mapping, or an actual export route.
- **[observed]** The current Export menu exposed CSV, RIS, BibTeX, Plain text, RefWorks (RIS), Zotero (RIS), EndNote (RIS), Mendeley, and SciVal. No download was activated.
- **[official_documentation]** Current Scopus Support search discovery reports different export-option caps, including 20,000 for non-Mendeley file options; the direct support route and account-specific behavior still require human verification.
- **[observed]** A broad CubeSat probe was discrepant: the current direct results page displayed 2,000 while same-session history exposed 8,930. **[untested]** This pilot cannot identify whether the discrepancy is a result cap, interface migration effect, or another count-scope difference. It is not a usable final total.

## 6. Failure/zero disposition and impact

- **[observed]** A native explicit no-documents message is a valid zero only for the successfully parsed BT2-03 diagnostic. The adapter error, unsubmitted BT2 transport timeout, malformed first identity extraction, and any future page/total/export/identity mismatch are failures with `total=null`, never zero.
- **[observed]** The first helper version misclassified A1 as zero because it matched the visible “10 results” page-size label; the ledger corrects this from the native 1–4 of 4 range. It also initially missed the native BT2-03 wording; a same-page inspection established the zero. These are local safe-summary parser defects, not Scopus behavior.
- **[protocol]** No partial prefix is a candidate set. This pilot has `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false`.
- **[protocol]** `S-C01` remains incomplete. No candidate MBSE terminology was tested, accepted, rejected, added to the dictionary, or added to any translation.
- **[inferred]** No protocol semantic change is proposed. The only source implementation refinement is the audit-backed, lossless BT2 cell union; it remains draft pending W/n and human route review.

## 7. Recommendation

**[inferred] Recommend `revise`, not acceptance.** Retain the current exact free-text queries and BT2 union as a draft. Before any acceptance, a human must resolve the current adapter failure and 2,000/8,930 discrepancy; confirm `W/n` counting; inspect actual export/capture and caps with restricted storage; validate full-cell completeness/identity reconciliation; establish any controlled-vocabulary hierarchy/scope before proposing descriptors; complete `S-C01`; and wait for `P-001` to set the common cutoff.
