# Web of Science X06 date-control retest

The corrected hydrated-control runner used one owned page and normal Basic Search route. Edition waiting/checkbox handling and English-row setup progressed, but the current date workflow stopped at `date_control_setup_failed` before query submit. Native submit/reissue counts are zero; total is `null`, not zero.

This live retest confirms the remaining blocker is the combined current Publication Date value surface shown in X05 (`All years (1900–2026)`), not edition selection. The patched Add Date Range helper did not yet open/configure that combined value control into exact date inputs. No record, screening, import, gate, or final event occurred. Lease cleanup/release and anchor preservation passed.

**No freeze.** A later X must interact visibly with the combined date-value control and retain exact 2011-01-01/2026-08-26 readback before one submit.
