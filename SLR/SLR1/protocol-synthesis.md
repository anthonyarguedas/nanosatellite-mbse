# Planned synthesis

Use a structured evidence map and narrative synthesis. Do not pool effect estimates because the models, outcomes, and evidence designs are expected to differ too much.

### Relationship to Buruso et al. (2026)

Buruso et al. (2026) is a broad secondary review of 126 selected space-MBSE studies and reports published from 2011 through 2023. It maps methods, languages, tools, five MBSE phases, and general challenges across many kinds of space work.

Use Buruso et al. only under the [Part 1 evidence restrictions](protocol.md#need-for-this-review), the [supporting prior-secondary-review protocol](protocol-prior-secondary-reviews.md), and the [Part 2 baseline and citation-search procedure](protocol-discovery-and-appraisal.md#completing-the-baseline-and-citation-searches).

This review is not an update or replication of Buruso et al. Do not compare the two reviews' counts as evidence of effectiveness.

For a descriptive view of currency and overlap, results may be split into 2011–2023, matching Buruso et al.'s evidence window, and 2024 through the common evidence cutoff. This split does not change eligibility or imply independence.

### RQ1

- Synthesize report context, EPS representation, grouped inputs and assumptions, grouped engineering results, implementation footprint, limitations, and evaluative RQ1 claims.
- Present Route A and Route B separately before combining them.
- Compare author labels such as *lightweight* or *scalable* with the extracted footprint and inline support.
- Present all `report_reuse_level` values as source-bounded report-level results. Synthesize resolved artifact lineages, applicability envelopes, reusable cores, variation points, tailoring methods, tailoring effort, assurance, independence, failures, demonstrated coverage, and `lineage_reuse_level` from the separate lineage-level records. Use lineage and consolidated-application denominators for deduplicated conclusions, and keep unresolved report-level cases visible.
- Keep method or workflow reuse separate from artifact reuse.

### RQ2

- Use only findings with `direct_synthesis = yes` for direct conclusions. Present near misses separately.
- Present claim kind and scope, role, category, author direction, evidence-supported direction, mechanism, measure directness, evidence basis, support, comparator adequacy and rival explanations when required, applicability, and lifecycle stage.
- Present assertion-only findings separately from executed, comparative, stakeholder, physical, operational, and independent-transfer evidence.
- Preserve source-reported values, units, denominators, uncertainty, and practical interpretation. Label reviewer-derived values.
- Keep benefits, null findings, adverse findings, and burdens visible without calculating a reviewer-defined net effect.

### RQ3

- Use only activities with `direct_synthesis = yes` for direct conclusions. Present system-wide co-occurrence and other near misses separately.
- Map target, bridge, V&V object, method, criterion, timing, execution, result, evidence basis, support, and later physical continuity.
- Keep EPS-specific and system-wide EPS-linked activities separate.
- Distinguish execution from validation and model-to-test closure.
- Record comparator adequacy and rival explanations only for comparative or causal V&V-effectiveness claims.

### Cross-cutting safeguards

- Apply the canonical units, denominator, and dependence rules in Part 1.
- Separate peer-reviewed reports from preprints, technical reports, and theses in descriptive or sensitivity views when useful.
- Apply the Part 2 [finding-support and conclusion-confidence framework](protocol-discovery-and-appraisal.md#finding-support-reporting-bias-assessment-and-conclusion-confidence).
- Use sensitivity views by route, evidence basis, support, measure directness, comparator adequacy when required, publication provenance, lineage confidence, reuse level, and artifact availability.
- Treat cross-tabulations as descriptive co-reporting unless extraction establishes a direct link.
- Treat sparse direct evidence as a result. Do not fill gaps with whole-spacecraft MBSE claims.

## Required new-run artifacts

Under the Part 1 restart policy, create these artifacts with provenance after task [`P-000`](TASKS.md) is complete. Track search infrastructure under [`S-001`](TASKS.md), extraction forms under `E-001`, and remaining artifacts under [`A-001`](TASKS.md):

- dated methods decision log.
- complete Part 2 discovery and screening artifact bundle.
- separate prior-secondary-review bundle.
- frozen report-level extraction codebook and schema.
- one extraction file per included report.
- report-family table.
- compiled report-level reuse-record and report-level application tables.
- separate artifact-lineage extraction table.
- separate consolidated tailoring-application table including effort and assurance.
- focused-audit log, discrepancy and adjudication log, deterministic-validation report, test–retest files, and supervisor-audit files when applicable.
- compiled report, report-level reuse, RQ2, RQ3, lineage-level reuse, and consolidated tailoring data.
- bibliography, analysis code, and derived-value scripts.
- machine-readable PRISMA count reconciliation, official PRISMA 2020 flow diagram, synthesis outputs, and completed PRISMA-S and PRISMA 2020 checklists.

Do not publish licensed exports, copyrighted abstracts, or full texts when rights prevent it. Publish or archive the methods, dates, schemas, decisions, derived counts, code, and a clear materials-availability statement.

## Completed-review reporting

The final report will:

- name every source used, search date, and common evidence cutoff.
- distinguish failed or planned-but-unused sources.
- link to exact source-native searches and PRISMA-S logs.
- report focused-audit, deterministic-validation, test–retest, and supervisor coverage exactly as performed.
- report the prior-secondary-review assessment separately.
- explain why no pooled effect estimate was used.
- label every count with its analytic denominator.
- cite apparently eligible full-text exclusions with source-located reasons.
- present evidence basis, finding support, reporting-bias considerations, reuse levels, and conclusion confidence under Part 2.
- report all protocol changes and departures.
- state access to the protocol, data, code, and materials.