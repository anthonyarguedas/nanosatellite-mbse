# Migrated OATD interface exploration

- **Session ID:** `S-D09-X00-20260825T152537-0400`
- **Status:** historical exploration migrated from an abandoned pre-two-mode retry chain
- **Accepted evidence:** no
- **Screening/import/final event:** none

## Question

Why did repeated advanced-form diagnostics fail before native submission?

## Real-page finding

A transient screenshot and bounded semantic DOM inspection found three page forms. The form whose action targets `/oatd/search-composer` was hidden and contained hidden `box1`, `field1`, and `input[type=submit]` controls. The only visible page-level submitter belonged to the separate basic-search form. Attempts to force values into the hidden advanced form failed readback and never issued a native submit.

The safe projection is retained in [`semantic-submit-inspection.json`](semantic-submit-inspection.json). No screenshot, raw DOM, page content, record, cookie, credential, or session value was retained.

## Disposition

The hidden home-page form is the wrong interaction target. Discard the experimental hidden-control patches and do not turn their failures into campaign evidence. The next exploration session should open the normal visible advanced composer route (or activate its visible source-owned control), then interact with its visible fields and submitter.

## Proposed next exploration

Use `S-D09-X01-<timestamp>` on one owned page:

1. open the visible advanced composer;
2. map visible title/query and submit controls;
3. retain a restricted screenshot and bounded semantic projection;
4. submit one small count-only sentinel;
5. observe transient challenge/loading/busy states under finite waits; and
6. freeze a working interaction recipe before any new evidence attempt.
