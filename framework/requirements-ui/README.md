# Requirements UI

A workbook inspired by Google Sheets, with a restrained n8n style. Each tab uses the same two editable tables. No build step or npm dependencies are needed.

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
- **Payload** has the Instrument and Processor and Memory definitions inside `PayloadSubsystem`.
- **Ground Station** has the eight subsystems declared in `GroundSegment`.
- **Orbit** stays in Mission. Assign mission requirements to it using **Affected domain elements**. It has no separate tab.

The three detailed tabs have an **Affected subsystems** or **Affected elements** column. Assignments use rows in the current left table. **Source** records provenance and can link to rows on any tab. These are separate relationships. For example, a bus requirement can derive from a mission requirement and be assigned to the Power subsystem.

The catalog is read from the generic mission model when the server starts. The generic model includes a `GroundStation` aggregate definition for its existing subsystem definitions. New mission files create domain and subsystem rows from this catalog. They contain no prefilled requirements.

Tab identity uses stable element keys. Renaming a domain updates its tab label and preserves its requirements, children and links. A new Bus, Payload or Ground Station instance gets its own tab using the same catalog and table UI. An element with child rows must be emptied before its type can change or it can be deleted. Browser reload restores the selected tab through the URL fragment.

## Tables

- Both ID columns are text fields. Stakeholder and domain element IDs have three uppercase letters, such as `LPR` or `ORB`. Statement IDs have three uppercase letters followed by three digits, such as `REQ001`. IDs are assigned automatically and remain editable.
- Enter stakeholders and choose Regulatory Agency, Mission Stakeholder, Launch Provider or Partner.
- External accepts requirements, needs, objectives, concerns and constraints. Its type dropdown is in the statement text cell. Other tabs list derived requirements.
- Dropdown cells use plain text and a small arrow at the right edge. Linked IDs are plain links with no pill background.
- **Source** links to individual rows anywhere in the workbook. Open the picker and check the rows to link. Click a linked ID to open its tab and focus that row. Source and assignment links survive ID changes. Source cycles are blocked across all tabs.
- Use variable names in braces in statement text, such as `{mass}`. Hover over the text for a preview with values substituted.
- Click **+** at the right of the table header to add a shared variable column. Variable columns and their types apply to all requirement tables. Choose **Integer** or **Float**. Click **Int** or **Float** beside a variable name to change its type. Integer values must be safe JavaScript integers. Float values must be finite. Empty values stay unset.
- **Verified** is a read-only result at the right edge of the cell. Click the cell or press F2 to edit its SysML condition. It cannot be toggled manually. A missing condition leaves the row unverified. Enter `true` or `false` only when you intend an explicit constant SysML condition.
- The **+** beside a table title inserts a row. Hover over a row to reveal its trash button in the left gutter. This deletes that row directly, regardless of selection. Remove its source and assignment links before deleting it. Rows with children remain protected.
- Tab moves between cells. Enter moves down. Shift reverses the direction. Shift+Tab from an ID cell focuses that row's trash button. Enter activates it. Alt+ArrowDown from External statement text opens its type selector. Alt+Enter inserts a line break in text.
- Headers use text labels. Click a column header to sort. Paste tab separated cells from Google Sheets in data column order, starting with ID. The delete gutter is separate from the data. Pasted sources and assignments accept comma separated row IDs or unique element names. The verification column accepts SysML expressions, including the lowercase literals `true` and `false`. Invalid grid pastes are rejected as a whole.

## Verification expressions

Use the current row's variable names directly. Use another statement's ID and a variable name for a reference, including statements on other tabs. IDs are unique across the workbook:

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
- Arithmetic `+`, `-`, `*`, `/`.
- Comparisons `<`, `<=`, `>`, `>=`, `==`, `!=`.
- Boolean literals `true`, `false` and operators `and`, `or`, `xor`, `implies`.

This is a restricted SysML expression subset. Function calls, units, assignments and other language features are rejected. JavaScript evaluates a parsed syntax tree in a worker. It never executes expression text with `eval` or `Function`. Expression length, token count and nesting are bounded.

Conditions must produce a Boolean. An unset value needed by the condition gives a pending result. Invalid syntax, unknown references, invalid types and nonfinite arithmetic give an error. Pending and error results use an indeterminate checkbox with details in its tooltip. Results recalculate when values change, including values in other rows.

Expression references use visible row IDs. Update a condition if you rename an ID it references. Source links use stable internal keys and remain intact.

## SysML storage

Edits save automatically to the selected mission file without a success toast. Saving and errors use a plain footer status. The app owns only the block between `// <requirements-ui>` and `// </requirements-ui>`. Content outside that block is preserved.

The block contains JSON for lossless UI round trips and a generated mission package that imports the generic models. Stakeholder and domain parts use their generic definitions. Subsystems are nested parts of their domain instance. Requirements are native requirement usages. Other External statement kinds are attribute usages with an explicit kind. Variable columns become optional `Integer` or `Real` attributes. Source links become SysML dependencies. Allocations become native `ref part affectedElements` references to domain or subsystem instances.

Valid verification expressions generate native SysML constraints. Cross row references are bound to the corresponding mission elements. Invalid draft expressions remain stored as text and produce no executable constraint. The browser's checkbox calculation is a lightweight evaluation of this subset. SysML tools remain responsible for full model validation.

Edit managed rows through the UI. Manual changes to generated elements do not update the JSON. Changes made by another editor or tab are detected before saving. Reload to use the latest version. Unsaved edits remain in the current tab until you save or leave it.

Versions 1 through 3 are upgraded on reading. Existing statements move into External when needed. Domain and subsystem instances are added from the generic catalog. Existing row keys, variables, conditions and values are preserved. Old checked rows without a condition become the explicit SysML condition `true`. Unchecked rows without a condition remain unverified. Manual verification flags are removed from the current format. The initial workspace was moved from the generic file into `framework/missions/mission.sysml`.

## Test

```sh
npm test
syside check ..
```

Tests use temporary files and leave project models unchanged.
