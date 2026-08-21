# ESA Indico interface-only diagnostic — 2026-08-20

- **Status:** diagnostic only; not an accepted pilot, final event, or source guideline.
- **Provenance:** moved from the pre-pilot task description when the new-run source-packet structure was created.
- **Required action:** independently revalidate every behavior used by `S-L02`.

The public `/search/` page exposed one free-text box and event, contribution, and material tabs. Its anonymous `/search/api/search` route returned one event for `satellite space`, zero for `satellite AND space`, zero for `satellite NOT space`, and one—not the union—for `satellite OR space`; common symbolic variants also reduced to the implicit-term result. The diagnostic therefore classified ESA Indico as a local-harvest source because the interface could not losslessly express all 11 direct partitions.

Contribution and material routes were visible, so the source must not be described as event schedules only. ESA's public general search, Publications listings, and Archives Portal descriptions were also inspected and appeared to be, respectively, a general website search, formal-reference listings, and an image/historical archive rather than replacements for the Indico event/contribution/material universe.

Relevant public routes noted for revalidation:

- <https://indico.esa.int/search/>
- <https://indico.esa.int/search/api/search>
- <https://www.esa.int/esearch>
- <https://www.esa.int/About_Us/ESA_Publications/ESA_Publications_listings>
- <https://historicalarchives.esa.int/how-search-and-credit>
