# Requirements UI

A workbook inspired by Google Sheets, with a restrained n8n style. Each tab has linked tables and a focused requirement editor. No build step or npm dependencies are needed.

## Run

Install Node.js 22 or later, then run from the repository root:

```sh
cd framework/requirements-ui
npm start
```

Open <http://127.0.0.1:3000>. Set `PORT` to use another port. The server only listens on the local machine.

The default mission file is `framework/missions/mission.sysml`. Choose another mission with `MISSION_FILE`, relative to the directory where you start the server:

```sh
MISSION_FILE=../missions/cubics.sysml npm start
```

A missing mission file is created automatically. Each file gets its own SysML package. The app imports generic definitions from `External`, `SpaceSegment`, `GroundSegment` and `Orbit`. Runtime edits leave the generic files unchanged.

## Tabs and allocation

- **External** has stakeholders on the left and their statements on the right. Existing data remains in this tab.
- **Mission** has Orbit, CubeSat Bus, Payload and Ground Station on the left. Its requirements have an **Affected domain elements** column for assignment to one or more of these rows.
- **CubeSat Bus** has the eight bus subsystems declared in `framework/mission.sysml`. Payload and the optional shared processor resource are separate from this list.
- **EPS** belongs to the bus's Power subsystem. Its left table lists Batteries, Solar Arrays, Processor and Memory, Regulators and Converters, Power Circuits and Switches, and Software from the generic model. Subdivide the EPS by adding component instances here. The right table holds parametric requirements with shared variable columns, SysML verification conditions, sources and an **Affected components** column.
- **Payload** has the Instrument and Processor and Memory definitions inside `PayloadSubsystem`.
- **Ground Station** has the eight subsystems declared in `GroundSegment`.
- **Orbit** stays in Mission. Assign mission requirements to it using **Affected domain elements**. It has no separate tab.

The detailed tabs have an **Affected subsystems**, **Affected elements** or **Affected components** column. Assignments use rows in the current left table. **Source** records provenance and can link to rows on any tab. These are separate relationships. For example, a bus requirement can derive from a mission requirement and be assigned to the Power subsystem.

The catalog is read from `framework/mission.sysml` and `framework/requirements.sysml` when the server starts. New mission files create domain and subsystem rows, plus the reusable orbit and EPS requirements. External stakeholder statements remain engineer supplied. The default workspace in `framework/missions/mission.sysml` has been reset to these generic rows. It contains no selected COTS components or entered mission inputs. Starting the app preserves subsequent mission edits.

Tab identity uses stable element keys. Renaming a domain updates its tab label and preserves its requirements, children and links. A new Bus, Payload, Ground Station or Power subsystem instance gets its own tab using the same catalog and table UI. Each new bus includes its own EPS tab and component instances. An element with child rows must be emptied before its type can change or it can be deleted. Browser reload restores the selected tab through the URL fragment.

## Editing a requirement

The default requirement table shows ID, source, read-only text, verification and assignments. Verified contains a calculated checkbox and a pencil. Both pencils open the same requirement modal. The verification pencil focuses its condition. Text and conditions are edited only in that modal.

Enter one verifiable statement. Enclose each variable name in `$$` to add its parameter row:

```text
The battery shall provide at least $$energy_J$$ J.
```

The `energy_J` row appears as soon as the closing `$$` is entered. Repeated names create one row. Names use letters, digits and underscores, begin with a letter or underscore, and follow the app's SysML identifier restrictions. Invalid or incomplete markers show an error and block saving.

The parameter matrix has three columns: **Name**, **Expression** and **Evaluated value**. Enter a number or SysML expression in its row, such as `2 * 3600` or `REQ001.energy_J * 1.2`. The modal includes the verification condition and a live text preview. Numeric types follow the model. Existing integer constraints remain enforced. Each requirement retains its own expression.

**Save requirement** applies the edit and triggers autosave. **Cancel** or Escape discards the modal's changes, including new parameters. Ctrl+Enter or Cmd+Enter saves. Existing parameter values and equation inputs stay accessible even when their names are absent from the text. Removing a marker preserves populated cells. Empty, unused names created during the current edit are discarded. Existing `{name}` placeholders remain supported for older data.

## Reusable sizing requirements

`framework/requirements.sysml` owns the generic requirement definitions and native constraints. Its annotations supply the table text, parameters, equations, sources and assignments. Mission files contain typed usages and mission inputs. Editing a mission leaves these generic definitions unchanged.

The workbook starts with 27 generic requirements. Mission has ORB001 through ORB003. EPS has SIZ001 through SIZ008, SIZ011, SIZ013, SIZ014, SIZ016, EPS002, EPS008, EPS009, EPS011, EPS019, EPS021, EPS047, EPS052, EPS053, EPS078, EPS088 and EPS089. Each requirement contains one sentence and at least one declared numeric parameter referenced in its text. Requirements without numeric parameters are excluded. IDs are preserved, so gaps are intentional. Separate obligations have their own rows, with **Source** links to the requirement they derive from. Generic `derivesFrom` annotations supply these links. IDs can differ when an existing mission already uses them. Each new Power subsystem gets independent EPS inputs and local equation links.

Requirement text references named `$$variables$$`. Their definitions and equations appear in the parameter matrix. For example, SIZ007 references `$$battery_min_J$$`, whose expression is `eclipse_energy_J / dod_max * (1 + degradation_margin)`. Entering mission inputs evaluates the text and its dependent parameters without changing the generic definitions.

Populate these inputs in order:

1. **ORB001:** `altitude_km`. The sourced reference Earth constants are `earthRadius_km = 6378` and `gravitationalParameter_km3_s2 = 398601`. They remain editable. ORB001 and ORB002 derive the orbit, sunlight and eclipse periods in seconds.
2. **SIZ001:** `sunlight_power_W`, `eclipse_power_W`, `sunlight_duty` and `eclipse_duty`. Use disjoint load totals. Already duty-weighted totals use duty 1. The row derives energy in joules.
3. **SIZ002:** `sunlight_efficiency` and `eclipse_efficiency`, each in (0, 1]. The row derives minimum panel power in watts.
4. **SIZ003:** `cell_eol_V` and `cell_eol_A` from compatible EOL conditions. **SIZ004:** `installed_cells`. Required physical counts round upward.
5. **SIZ005:** `lifetime_years` and `days_per_year`. Orbits per day derive from the orbit period. The preliminary assumption is one nominal battery cycle per orbit.
6. **SIZ006:** sourced `cycle_a`, `cycle_b`, `fit_dod_min`, `fit_dod_max` and selected `dod_max`. The decreasing power-law fit requires `a > 0` and `b < 0`. The selected DoD must be inside its sourced fit domain and support the required cycles. No chemistry or fit coefficients are assumed.
7. **SIZ007:** `degradation_margin`. Minimum battery energy is `E_e / DoD * (1 + M)` in joules. **SIZ008:** `pack_bol_J` and applicable `retained_energy_factor`. Convert Wh to J by multiplying by 3600. Margin enters preliminary sizing once. Retained capacity is derived separately.

Every expression cell in the modal stores an editable SysML expression. A literal such as `500` and an equation such as `2 * pi * sqrt(x)` use the same representation. The expression stays visible beside its evaluated value. You can edit or replace any prefilled equation. Editing a cell recalculates dependent values across tabs. Empty cells stay unset. Expressions that depend on empty cells show Pending. Syntax, reference, type and arithmetic errors appear in the affected cell with details in its tooltip. Insufficient cell counts, cycle life or capacity remain visible through the requirement conditions. Conditions also check that edited derived expressions still satisfy the generic sizing equations. Mission altitude, lifetime, duty cycles, efficiencies, selected products and margins have no default values. Existing free-text orbit statements are preserved. They do not silently supply sizing inputs.

These equations implement the preliminary circular orbit case in `final_report/design-proposal.tex`. They establish no seasonal illumination, peak-current, thermal or survival compliance. The retained EPS requirements cover generation, battery capacity and cycling, energy closure, mass, volume, memory and processor utilization. Each row retains its report source. Report criteria without defined numeric parameters remain in the report and are excluded from the workbook and generic requirement library. Complete scenario assessments remain unverified until applicable evidence and verification conditions are supplied. Native generic definitions retain their numerical and assessment predicates for a full SysML tool to bind and assess. Missing Boolean evidence inputs stay unbound in exports.

Click **Export mission SysML v2** in the requirements table header to download the whole current mission, including unsaved valid inputs. The export contains native typed requirements, equations, provenance, assignments, dependencies and bindings to the Orbit instance. Load it with the generic `framework/*.sysml` files and the standard SysML libraries. It has its own export package and excludes UI JSON. Unset inputs remain unbound. Invalid syntax, references, cyclic equations and nonfinite arithmetic block export. A download establishes no verification or qualification claim.

## Tables

- Both ID columns are text fields. Stakeholder and domain element IDs have three uppercase letters, such as `LPR` or `ORB`. Statement IDs have three uppercase letters followed by three digits, such as `REQ001`. IDs are assigned automatically and remain editable.
- Enter stakeholders and choose Regulatory Agency, Mission Stakeholder, Launch Provider or Partner.
- External accepts requirements, needs, objectives, concerns and constraints. Its statement type dropdown is in the requirement editor. Other tabs list derived requirements.
- Dropdown cells use plain text and a small arrow at the right edge. Linked IDs are plain links with no pill background.
- **Source** links to individual rows anywhere in the workbook. Open the picker and check the rows to link. Click a linked ID to open its tab and focus that row. Source and assignment links survive ID changes. Source cycles are blocked across all tabs.
- Write `$$mass$$` in the modal's requirement text to add a parameter row. The list and modal preview substitute evaluated values. Unset values retain their markers.
- Numeric expressions retain the model's declared types. Integer results must be safe JavaScript integers. Real results must be finite. Clearing an expression leaves the parameter unset.
- **Verified** shows a read-only checkbox and a pencil. Click the pencil or press F2 to open the requirement modal at its condition. The checkbox cannot be toggled manually. A missing condition leaves the row unverified. Enter `true` or `false` only when you intend an explicit constant SysML condition.
- The **+** beside a table title inserts a row. Hover over a row to reveal its trash button in the left gutter. This deletes that row directly, regardless of selection. Remove its source and assignment links before deleting it. Rows with children remain protected.
- Tab moves between cells and their edit buttons. Enter moves down in ordinary fields. Enter, Space or F2 on requirement text opens its editor. Shift reverses navigation. Shift+Tab from an ID cell focuses that row's trash button. Enter activates it. Requirement text supports line breaks inside the modal.
- Headers use text labels. Click a column header to sort. Paste tab separated cells from Google Sheets in data column order, starting with ID. The delete gutter is separate from the data. Pasted sources and assignments accept comma separated row IDs or unique element names. Text and verification cells accept edits only through the modal. Grid pastes that would overwrite them are rejected as a whole. Paste a single column of expressions down the modal's parameter rows. Invalid expressions remain drafts and show cell errors.

## Parameter and verification expressions

Parameters accept numeric expressions without an assignment or leading `=`:

```sysml
12
1.2e3
mass * 2
REQ002.mass / 2
RealFunctions::sqrt(x)
```

Use a Boolean expression in **Verified** to check a requirement. Use the current row's variable names directly. Use another statement's ID and a variable name for a reference, including statements on other tabs. IDs are unique across the workbook:

```sysml
mass <= 2.5
mass <= NED001.mass and cell_count >= 3
not (x > 10) or y == 0
x >= 0 implies x <= REQ002.x
```

Supported syntax:

- Finite numeric literals, including scientific notation.
- Variable names and `ROW001.variable` references.
- Parentheses and unary `+`, `-`, `not`.
- Arithmetic `+`, `-`, `*`, `/`, `^` and `**` (power, with right association).
- Comparisons `<`, `<=`, `>`, `>=`, `==`, `!=`.
- Boolean literals `true`, `false` and operators `and`, `or`, `xor`, `implies`.
- The constant `pi` and the bounded function set `sqrt(x)`, `arccos(x)`, `floor(x)`, `abs(x)`, `min(x, y)` and `max(x, y)`. The qualified forms `TrigFunctions::pi`, `RealFunctions::sqrt`, `TrigFunctions::arccos`, `RealFunctions::floor`, `RealFunctions::abs`, `RealFunctions::min` and `RealFunctions::max` are also accepted. Trigonometric arguments and results use radians. Upward rounding uses `-floor(-x)`.

This is a restricted SysML expression subset. Other function calls, units, assignments and other language features are rejected. JavaScript evaluates a parsed syntax tree in a worker. It never executes expression text with `eval` or `Function`. Expression length, token count and nesting are bounded.

Parameter expressions must produce numbers of their model's declared type. Conditions must produce a Boolean. Parameters are evaluated even when the row has no verification condition. An unset dependency gives a pending result. Cycles, invalid syntax, unknown references, invalid result types and nonfinite arithmetic give an error. A parameter error appears beside its expression. Pending and error conditions use an indeterminate checkbox with details in its tooltip. Results recalculate when expressions change, including references to other rows.

Expression references use visible row IDs. Renaming an ID through the UI updates condition and equation references. Source links use stable internal keys and remain intact.

## SysML storage

Edits save automatically to the selected mission file without a success toast. Saving and errors use a plain footer status. The app owns only the block between `// <requirements-ui>` and `// </requirements-ui>`. Content outside that block is preserved.

The block contains JSON for lossless UI round trips and a generated mission package that imports the generic models. Stakeholder and domain parts use their generic definitions. Subsystems are nested parts of their domain instance. EPS components are nested inside their Power subsystem instance. Requirements are native requirement usages. Other External statement kinds are attribute usages with an explicit kind. Variable columns become optional `Integer` or `Real` attributes. Source links become SysML dependencies. Allocations become native `ref part affectedElements` references to domain or subsystem instances.

Valid parameter expressions generate native attribute bindings. Their equations are exported instead of their calculated values. Integer bindings retain an integrality constraint when conversion is needed. Verification expressions generate native SysML constraints. Cross row references are bound to the corresponding mission elements. Invalid draft parameter expressions remain in the UI data without an executable binding. Invalid draft conditions produce no executable constraint. The browser's checkbox calculation is a lightweight evaluation of this subset. SysML tools remain responsible for full model validation.

Edit managed rows through the UI. Manual changes to generated elements do not update the JSON. Changes made by another editor or tab are detected before saving. Reload to use the latest version. Unsaved edits remain in the current tab until you save or leave it.

Versions 1 through 7 are upgraded on reading. Existing statements move into External when needed. Domain and subsystem instances are added from the generic catalog. Existing row keys, variables, conditions and values are preserved. Old checked rows without a condition become the explicit SysML condition `true`. Unchecked rows without a condition remain unverified. Manual verification flags are removed from the current format. Version 5 adds the default EPS components to existing Power subsystem instances once. Version 6 adds COTS selections. Version 7 seeds generic requirements and their parameters once. Version 8 converts numeric values to literal expression text and moves separate formula maps into their parameter cells. Existing equations become directly editable. The entered expression is preserved across saves. Calculated results are never stored in its place. Upgrades preserve existing row keys, values, conditions, components and links. They allocate unused IDs when needed and leave the file unchanged until save. Requirement and component deletions persist across reloads. The initial workspace was moved from the generic file into `framework/missions/mission.sysml`.

## Test

```sh
npm test
syside check ..
```

Tests use temporary files and leave project models unchanged. An optional browser test exercises the modal, cancellation, generated columns, evaluation, persistence and download:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs npm test
```
