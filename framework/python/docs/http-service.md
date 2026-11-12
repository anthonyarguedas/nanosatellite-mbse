# Native application service

The HTTP bridge delegates domain work to `nanosat_mbse.service.Application`.
The application retains trusted native graphs, draft handles, callable registries and execution evidence.
The browser projection supplies edits and display data.
It never becomes the backing model.

## Launch

From a source checkout, the Node bridge launches:

```sh
python3 -I -B -u framework/python/service.py --model /path/to/mission.py
```

An installed deployment can launch:

```sh
python3 -I -B -u -m nanosat_mbse.service \
  --model /path/to/mission.py \
  --cots-directory /path/to/cots
```

Without `--model` or `MISSION_FILE`, the service uses `framework/sessions/current.py` in a source checkout.
Outside a checkout it uses `sessions/current.py` under the working directory.
The UI and native CLI use this same location policy.
Optional trusted launcher arguments are `--sessions` and `--scripts-directory`.
Paths, providers and interpreter arguments are unavailable as browser operations.
The source bootstrap adds only its own `src` directory.
The service uses no old UI worker modules.

`requirements-ui/server.mjs` remains the `npm start` compatibility entry point.
`requirements-ui/server/server.mjs` handles HTTP and static files.
`requirements-ui/server/python-client.mjs` supervises the native worker.
The worker accepts bounded JSON lines with positive integer request IDs.
One application job runs at a time.
The reader accepts separate cancellation packets while analysis execution runs.

## Storage selection

The current workspace accepts a `.py` path or a retained legacy `.json` source.
The service prefers an existing adjacent `.py` file.
The first legacy open converts JSON to a new Python file without changing the JSON.
A selected path with neither a native session nor a legacy source creates an empty `Session`.
New named sessions are also blank, and existing sessions are reused through Save as.
The supplied Generic EPS Example is an ordinary saved session with no regeneration path.
A new `<stem>.metadata.json` records that the native current session exists.
A missing authoritative file with that metadata produces an error, including after restart.
It is never regenerated from stale JSON.

Creation requests accept `template: "blank"` or `template: "copy"`.
The removed `generic-eps` creation value is rejected.
Historical `generic-eps` metadata remains readable as provenance only.

Default session storage uses:

```text
framework/sessions/current.py
framework/sessions/current.metadata.json
framework/sessions/<uuid>/session.py
framework/sessions/<uuid>/metadata.json
```

For a custom workspace, named sessions use its neighboring `sessions/` directory.
A workspace already inside a directory named `sessions` shares that directory with named sessions.
An explicit `--sessions` directory overrides this convention.
A legacy named session is converted on first open.
Its old `session.json` and `<uuid>.json` remain unchanged.
The native metadata retains its ID, name, template and creation time.
A missing native named session remains missing.
Session creation uses a create-only folder workflow and a directory creation lock.
All model saves use the same `SessionRepository` as the REPL.

Python session files are trusted local code.
The service never accepts file contents or import paths from the browser.
Handwritten files without the canonical marker remain read-only for replacement and require Save as.

## Handle and revision contracts

Opening a session returns:

```json
{
  "workspace": {},
  "handle": "opaque-native-draft-capability",
  "revision": "path-bound-file-revision",
  "storage": "python",
  "writable": true,
  "session": {"id": "current", "name": "Current session"},
  "metadata": {},
  "catalog": [],
  "products": [],
  "calculationSignature": "native-calculation-identity",
  "protocolVersion": 1
}
```

The workspace in this abbreviated example is the full version-14 projection in actual responses.
Keep its `modelState` metadata through local draft copies.
Native callable cells contain read-only, slot-scoped descriptors issued by a trusted `CallableRegistry`.
There is no endpoint that imports a browser-provided class or callable.

A handle identifies an independent native graph and its browser lineage.
A file revision authorizes a save to one stored path.
They serve different purposes.
Opening twice creates independent handles and execution lineages.
Draft operations produce a new handle without writing the file.
Apply only the response matching the current client generation.
Store its handle together with the returned canonical workspace and workbook metadata.
The service bounds handle and evidence stores and expires them after four hours.
An expired handle produces HTTP 410.
A worker restart likewise requires a fresh open.

`POST /api/draft` accepts:

```json
{"handle": "opened-handle", "workspace": {}}
```

It applies differences to a trusted native clone through Session and domain methods.
The actual request workspace contains the full edited projection.
Normal add hooks create elements, component requirements and budgets.
Renames rewrite references in Python.
Removal uses native child, scope, expression and relationship protection.
Owned parameters and concrete custom classes remain on the original native graph lineage.
Native source round trips make detached clones without reconstructing them from browser rows.

`modelState` seed history and generic subject relationships are retained from the trusted graph.
Browser metadata cannot override lifecycle history.
Callable descriptors can only repeat a previously registered capability for the exact binding slot.
Normal snapshot edits cannot silently erase an undisplayed native condition.
Use explicit native commands to replace or remove native bindings.

Unused visual placeholders are excluded from application objects.
Malformed expression drafts retain their source and evaluate with cell diagnostics.
Invalid incomplete structural edits return a validation error and leave the previous handle intact.
Keep those raw editor drafts in the browser until the engineer corrects them.

Saving uses:

```json
{"handle": "draft-handle", "revision": "opened-file-revision"}
```

Send it to `PUT /api/workspace?session=<id>`.
An optional `workspace` applies its edits first.
Install the returned canonical workspace, handle, metadata and new revision.
Do not mark the submitted JSON as the new saved model.
A stale REPL or browser writer produces HTTP 409 and retains local draft handles.
Use reload or Save as for recovery.

The browser retains an explicit handle in every workbook and editor draft.
Domain requests without a handle are rejected.
A description request without a handle explicitly opens the selected session.
Native callable cells retain their scoped read-only descriptors through edits and saves.

## Operations

| HTTP route | Native operation | Result |
| --- | --- | --- |
| `GET /api/workspace?session=<id>` | `open` | Native session view |
| `PUT /api/workspace?session=<id>` | `save` | Saved canonical view |
| `GET /api/sessions` | `sessions` | Picker metadata |
| `POST /api/sessions` | `create` | Blank session or independent Save as copy |
| `POST /api/draft` | `draft` | Canonical unsaved view |
| `POST /api/commands` | `command` | Canonical native command result |
| `GET` or `POST /api/describe` | `describe` | Current view and workbook metadata |
| `POST /api/evaluate` | `evaluate` | Common native cell and verification results |
| `GET /api/scripts` | `scripts` | Python-declared registered definitions |
| `POST /api/scripts/run` | `run` | Display evidence plus opaque evidence token |
| `GET /api/catalog` | `catalog` | Python framework catalog |
| `GET /api/products` | `products` | Current database products |
| `GET /api/cots?product=<id>` | `cots_facts` | Current sourced facts |
| `POST /api/python?session=<id>` | `export_python` | Executable Python configuration download |
| `POST /api/json?session=<id>` | `export_json` | Explicit legacy transport projection download |
| `POST /api/kicad` or `/api/fprime` | `artifacts` | Python-validated data for JS output adapters |

`GET /api/describe?handle=<token>` also works for a named session without a session query parameter.
Post requests can carry `session` where relevant.
The workspace save route deliberately binds the handle to its selected session ID.

Native commands use this shape:

```json
{
  "handle": "draft-handle",
  "command": {
    "name": "add_element",
    "owner": "mission",
    "definition": "SpaceSegment::CubeSat"
  }
}
```

Available command names are `add_element`, `add_stakeholder`, `add_cots`, `add_script`, `add_requirement`, `remove`, `rename`, `retype`, `substitute_product`, `set_value`, `set_expression`, `set_unit`, `replace_binding`, `set_property`, `configure_component`, `set_text`, `set_relationships`, `set_verifications`, `select_fact`, `set_facts`, `add_mode`, `rename_mode`, `remove_mode`, `configure_mode`, `configure_load`, `connect_power`, `disconnect_power` and `update_definition`.
Commands use registered object keys or visible IDs for `target`.
They accept primitive values, restricted expression source and known definition identities.
No command accepts Python module paths or executable source files.

`set_property` takes `target`, a declared `property` name and a scalar `value` for a generic component.
COTS properties use `select_fact` with their canonical property reference name.
`configure_component` takes `target` and optional `quantity` and `requirements` fields.
Its requirement keys edit the same authoritative assignments used by the COTS table.
The quantity weights assignment sums and defaults to one.
COTS projection rows retain this optional `quantity` field.
Generic literal properties and assignments round trip through `modelState.componentProperties` and `modelState.componentAssignments`.
COTS facts remain pins, and their assignments remain in the component row.
Metadata includes `propertyTypes`, `assignmentFunctions` and each COTS object's `genericTypes` and `componentProperties`.
The existing condition editor accepts `all_assigned`, `sum_assigned` and `count_assigned` without accepting arbitrary Python class paths.

## Evidence

Run a configured instance explicitly:

```json
{"handle": "draft-handle", "script": "SCR001"}
```

`POST /api/scripts/run` calls `Session.run()` with the native isolated runner.
The response retains the existing `signature`, `cotsSignature` and `runs` fields for display.
It also returns `handle`, `evidenceToken`, `calculationSignature` and `evidenceCurrent`.
The returned run records contain outputs and logs for presentation only.

Recalculate checks with:

```json
{"handle": "returned-handle", "evidenceToken": "returned-evidence-token"}
```

`POST /api/evaluate` resolves evidence from the service cache.
It ignores caller copies of run records when a valid token is present.
Untrusted run values without a token are rejected.
A token belongs to one browser lineage.
Copies and independently reopened sessions need fresh execution.
Calculation, source and pinned COTS freshness checks use the native evaluation context.
Unrelated new database rows leave selected fact evidence current.

Evaluation returns `results`, `scripts`, `engine`, `cotsSignature`, native `components`, `handle`, `calculationSignature` and `evidenceCurrent`.
It also returns a canonical `view` containing the workspace, handle and workbook metadata.
Install that view only for the current client generation so new Python-generated rows and IDs accompany the handle.
Component results come from the same `DatabaseBacked.assess()` and `verify()` API available to native callers.
Compare the native signature and server freshness result, never the old JS `scriptContext()` string.
The service does not execute an analysis during open, draft, save, export or automatic evaluation.

The supervisor bounds requests to 8 MiB, responses to 16 MiB and waiting jobs to 16.
A run has a native 30-second total budget and the HTTP bridge permits two active run requests.
The native runner owns per-script timeout, output limits and process-group cleanup.
HTTP abort sends cancellation to the live worker before any forced restart.
A normal cancellation preserves the worker and its handles.
A malformed response, active timeout or crash replaces the process and revokes handles.

## Browser client

`public/native-client.js` transports native handles and evidence tokens.
`public/workbook.js` handles detached projections, provisional controls and three-way editor merges.
Editors live in `public/editors/`.
They use Python metadata for tabs, allowed definitions, parameter ownership, source candidates, load accounting and limits.
The browser retains invalid raw drafts while Python reports validation errors.
Canonical responses are rebased against newer typing, with generation checks for evaluations and serialized native commits.

Mode-split parameter rows travel as `stateEdits` alongside the workspace:

```json
{"target": "requirement-key", "parameter": "power_W", "values": {"mode-key": "3"}, "lastEdited": "mode-key", "merge": false}
```

An omitted `values` mapping splits the shared expression.
`merge: true` selects the last edited branch through `Session.configure_parameter_states()`.
Python creates the conditional source and applies the same rule to native callers.
The browser only projects returned branches into rows.

COTS reference renames and suspended requirement drafts are rebased through native operations.
Script creation, updates and deletion use registered native commands.
Run responses retain the complete server evidence token and diagnostics.
The primary download is an executable Python session.

Superseded root JS rule modules, duplicate built-in scripts and the old worker have been removed.
Node exporters under `server/exporters/` format native-validated data and native verification results.
They provide no fallback validation or domain calculation engine.

## Native CLI composition

Local tools can call `Application.load_session()` to obtain a trusted native graph and `Application.create_session(graph, name=...)` to publish an independent named copy.
These use the same repository and creation lock as HTTP session operations.
The `nanosat-mbse analysis` and `report` commands use native bench factories and these shared operations.
They create configuration only and never execute analyses as a creation side effect.
