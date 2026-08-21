# NTRS interface-only diagnostic — 2026-08-20

- **Status:** diagnostic only; not an accepted pilot, final event, or source guideline.
- **Provenance:** moved from the pre-pilot task description when the new-run source-packet structure was created.
- **Required action:** independently revalidate every behavior before accepting `S-D13`.

The public interface/API accepted the grouped expression `(CubeSat\|nanosatellite)+MBSE`. NASA's public search tips at <https://sti.nasa.gov/search-tips-for-the-nasa-sti-repository/> described `+` for AND, `\|` for OR, `-` for NOT, quoted phrases, prefix wildcards, and parentheses. The pilot must independently validate those semantics, all 11 translations, any query-length limit, fields, date and language handling, pagination/export, stable identity, completeness, and failure rules.
