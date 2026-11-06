# Requirements UI

A workbook inspired by Google Sheets, with a restrained n8n style. Each tab has linked tables and a focused requirement editor. No build step or npm dependencies are needed.

## Run

Install Node.js 22 or later and Python 3.8 or later, then run from the repository root:

```sh
cd framework/requirements-ui
npm start
```

Open <http://127.0.0.1:3000>. Set `PORT` to use another port. The server only listens on the local machine.

The default workspace is `framework/missions/mission.json`. Choose another file with `MISSION_FILE`, relative to the directory where you start the server:

```sh
MISSION_FILE=../missions/cubics.json npm start
```

A missing workspace is created as plain JSON. Only `.json` workspace paths and the current schema are supported. The existing mission and saved sessions have already been converted to the current format.

## Python worker

Automatic parameter calculations, verification methods, power projections and registered script inputs run in a persistent Python worker. The browser UI and Node HTTP server remain in place. The browser worker transports JSON to `POST /api/evaluate` and contains no calculation engine. `worker/models.py` defines the request-local parameter, requirement, script and workspace models. `worker/expressions.py` owns Python parsing and evaluation.

Set `VERIFICATION_PYTHON` to select a Python executable or virtual environment. The interpreter starts lazily and stays available across requests. Each request receives a fresh model, dependency cache and execution context. Only bounded, source-only syntax trees are cached between requests. Different tabs and sessions share no calculation values or Python variables. A missing interpreter produces an actionable error and no JavaScript fallback.

Requests use JSON lines over stdin and stdout. The Node supervisor serializes requests, permits up to 16 waiting requests, and enforces a 4-second execution timeout. A timeout, active cancellation, crash, malformed response or oversized response replaces the process. Requests are limited to 8 MiB and responses to 16 MiB. Browser requests carry generation IDs and discard superseded responses.

Version 14 workspaces use plain JSON with `expressionLanguage: "python"`. Python source retains its spelling. Invalid drafts remain editable and produce cell errors. No expression converter or older format importer is present. Script source runs only through an explicit **Run Python** action in a separate process.

The Python catalog now owns the workbook's 52 element types and 27 reusable requirement definitions. `worker/catalog_data.py` contains the maintained definitions, `worker/catalog_models.py` their typed models, and `worker/catalog.py` their validation and UI projection. The catalog uses no external model files. Stable identifiers such as `SpaceSegment::CubeSat` and `FrameworkRequirements::OrbitPeriod` are opaque data keys that preserve workspace links.

The download is **Export workspace JSON** in the requirements table header. It includes valid unsaved editor inputs and changes no session data. Framework SysML files, importers, exporters, conversion utilities and old schema migrations have been removed. Existing mission and named-session data is preserved in JSON.

## Sessions

Use the session toolbar above the workbook:

- **New session → Blank** starts with empty tables and no preloaded elements or requirements.
- **New session → Generic EPS** starts with the generic mission hierarchy, 27 orbit and EPS requirements, units, rationale and sizing equations. Mission inputs are unset. The sourced Earth constants remain populated.
- **Save as…** saves an independent named copy of the current workspace. It includes unsaved edits in the requirement pane without applying those pane edits to the original session.
- The **Session** picker reopens saved workspaces. The existing mission remains listed as **Current mission**.

Each saved session autosaves independently. Names contain 1 to 80 characters and are unique without regard to letter case. Creating another Generic EPS session always starts from the framework templates. It leaves previous sessions unchanged.

Switching sessions waits for pending autosaves and asks before discarding an unsaved requirement draft. Save or correct invalid table edits before switching. A save conflict keeps the current session open. Save as can preserve a valid local workspace in a separate session when the original has a conflict.

The page URL contains the session ID and selected tab, so it can be bookmarked or reloaded. Session selection is local to each browser tab. Opening another session in one browser tab leaves other tabs on their own sessions.

Saved sessions live in `framework/missions/sessions/<id>/<id>.json`. A neighboring `session.json` stores the display name, template and JSON storage marker. With a custom `MISSION_FILE`, sessions live in a `sessions` directory beside the workspace. Named sessions retain their IDs and names. A missing JSON session stays missing and is never regenerated.

## Tabs and allocation

- **External** has stakeholders on the left and their statements on the right. Existing data remains in this tab.
- **Mission** has Orbit, CubeSat Bus, Payload and Ground Station on the left. It defines spacecraft modes and system power limits. Its requirements have an **Affected domain elements** column for assignment to one or more of these rows.
- **CubeSat Bus** has the eight bus subsystems declared in the Python catalog. Each subsystem has its own tab and CSRM generic component table, using the same add, rename and type selection UX as EPS. Use the arrow beside a subsystem name to open it. Payload and the optional shared processor resource are separate from this list.
- **EPS** belongs to the bus's Power subsystem. Its left table lists Batteries, Solar Arrays, Processor and Memory, Regulators and Converters, Power Circuits and Switches, and Software from the generic model. Subdivide the EPS by adding component instances here. The right table holds parametric requirements with shared variable columns, Python verification conditions, sources and an **Affected components** column.
- **Payload** has the Instrument and Processor and Memory definitions inside `PayloadSubsystem`.
- **Ground Station** has the eight subsystems declared in `GroundSegment`.
- **Orbit** stays in Mission. Assign mission requirements to it using **Affected domain elements**. It has no separate tab.

The detailed tabs have an **Affected subsystems**, **Affected elements** or **Affected components** column. Assignments use rows in the current left table. **Source** records provenance and can link to rows on any tab. These are separate relationships. For example, a bus requirement can derive from a mission requirement and be assigned to the Power subsystem.

The server loads the Python catalog through the supervised worker. New workspaces create domain and subsystem rows, plus reusable orbit and EPS requirements. External stakeholder statements remain engineer supplied. Starting the app preserves saved requirements, mission inputs, scripts and COTS selections. Editing the Python definitions and restarting the server updates the catalog without parsing a SysML model.

Tab identity uses stable element keys. Renaming a domain updates its tab label and preserves its requirements, children and links. A new Bus, Payload, Ground Station or Power subsystem instance gets its own tab using the same catalog and table UI. Each new bus includes its own EPS tab and component instances. An element with child rows must be emptied before its type can change or it can be deleted. Browser reload restores the selected tab through the URL fragment.

## Component states and power consumption

Each definition has one editing location. Other tables reference it by its stable key and display ID or mode name. Named COTS selection remains exclusive to EPS.

1. In a subsystem's generic component table, use the pencil beside the component name to open its editor. Define quantity, accounting and operating states there. The **Component States** table holds per-unit power in W, value meaning, source and operating conditions. It uses the workbook's plus button, trailing empty row and delete gutter.
2. In **Mission**, define spacecraft modes and their sunlight and eclipse shares in **Spacecraft Modes**. Each period must total 100%. Enter the system power limit in its single **PWR** requirement.
3. Each spacecraft subsystem tab, including Payload and EPS, owns one **PWS** subsystem limit and one **PWC** allocation per counted component. Enter `power_limit_W` as a shared expression or a conditional expression such as `18 if mode == "Downlink" else 3`. Their Source links form **PWR → PWS → PWC**. Limits stay independently assigned when a parent limit changes.
4. In that subsystem's **Component State Allocation** table, select each included component's state for each spacecraft mode. The table references locally owned component IDs and the modes defined in Mission. Component draws, quantities and accounting remain in the component editor.
5. In **EPS**, open the generic **LoadEnergy** requirement (normally SIZ001). Set **Load input source** to **Component modes** and select its **Load domains** by ID. Save the requirement to apply the connection. Selecting **Manual expressions** restores the four prior load inputs. Cancel discards a source or domain change along with the rest of the requirement draft.

Each power requirement covers all spacecraft modes. Adding a mode preserves the requirement rows and IDs. `allocated_power_W` starts with a reference that sums the child limits in the current mode. `draw_power_W` starts with a reference that sums their draws in that mode. Both expressions are editable. You can add calculations or mode conditions, replace the reference, or clear the cell. Parent requirements check the allocation sum and draw against their assigned limit. Component requirements check quantity times the selected state draw against their component allocation. Verification covers every configured mode, including modes with zero sunlight or eclipse share. Empty limits remain unset. Missing limits and missing state draws keep the affected checks pending. Complete checks return false for over allocation or an excessive draw.

Software is counted through its execution host. Its component editor references an existing Processor and Memory usage by ID. Passive structural and thermal elements, battery storage, and solar generation start excluded from load demand. EPS internal demand can be defined in its own generic component usages. Accounting rationale identifies any excluded or already covered demand.

A connected LoadEnergy requirement uses `LoadBudget.sunlight_power_W` and `LoadBudget.eclipse_power_W`. Its two duty factors are one because these averages already include the mode shares. Expressions, evaluated averages, energy and verification remain in the existing parametric requirement UI. There is no separate sizing summary. Missing states, missing power, or incomplete mode shares keep the affected parameters pending. A mode with zero share needs no draw to evaluate that period.

Component edits have **Save component** and **Cancel**. Cmd+Enter or Ctrl+Enter saves. Save as includes an unsaved valid component draft in the independent copy. Sessions retain their own modes, mappings, sources and EPS connections. Version 9 adds the CSRM component tables. Version 10 introduced power limit requirements. Version 11 merges their mode copies into one requirement per scope. Differing inputs become conditional expressions. Each merged requirement keeps its first key and ID. Source links, COTS links and expression references are redirected to it. Differing prose and rationale are retained in its rationale. Draws, mappings and EPS connections remain unchanged. Later deletions remain deleted.

The Python catalog declares optional `power_consumption_W` and `power_consumption` properties in W on spacecraft subsystems and components. The Python worker calculates allocations, component draws and weighted illumination budgets. Software demand remains assigned to its execution host.

This first view assesses preliminary steady load energy. Mode shares establish no chronological ordering or simultaneous peak demand. Startup pulses, rail limits, converter path losses, battery time histories and energy closure require their separate report assessments. A typical or estimated consumption value establishes no guaranteed hardware limit.

## Editing a requirement

The default requirement table shows ID, source, read-only text, verification and assignments. Verified contains a calculated checkbox and a pencil. Both pencils open the same right pane. The verification pencil focuses the first condition in **Verification methods**. Text and conditions are edited only in that pane. The workbook stays readable and interactive. Switching tabs keeps the draft open. On narrow screens the editor sits below the workbook.

Enter one verifiable statement. Enclose each variable name in `$$` to add its parameter row:

```text
The battery shall provide at least $$energy_J$$.
```

The `energy_J` row appears as soon as the closing `$$` is entered. Repeated names create one row. Names use letters, digits and underscores, begin with a letter or underscore, and follow the app's Python parameter identifier restrictions. Invalid or incomplete markers show an error and block saving.

**Rationale** is an editable field visible only in the pane. It starts with the requirement's provenance, such as `final_report/design-proposal.tex#eq:orbit-period (handpicked-0003, Eqs. 1-4)`. It supports source references and explanatory text up to 10,000 characters. Saving retains the rationale. Cancel discards its edits. Clearing it saves an empty rationale. The original provenance remains preserved in the model.

The parameter matrix has five columns: **Name**, **State**, **Expression**, **Units** and **Evaluated value**. Enter a number or Python expression in its row, such as `2 * 3600` or `REQ001.energy_J * 1.2`. Expression fields wrap and grow to show the full text. Enter units separately, such as `J` or `m^2/s^2`. Units are shared by variable name across the workspace. They are display labels and leave numeric evaluation unchanged. The pane includes the verification method table and evaluated parameter values. Verification feedback shows green **TRUE** or red **FALSE** without repeating the expression. Errors appear below the input in yellow with their message. **PENDING** indicates an unresolved result. An empty condition has no feedback label. Numeric types follow the model. Existing integer constraints remain enforced. Each requirement retains its own expression.

**State** starts at **All states**. Its options use the spacecraft modes defined in Mission. Selecting a state splits that parameter into one expression row per mode, initially retaining the shared expression in every row. Each row evaluates in its own mode. Units remain shared across these rows. Selecting **All states** in any split row merges the parameter using the most recently edited expression, including an empty expression. This merge choice survives saving and reloading. Existing mode conditionals also open as state rows. The app stores one Python conditional expression for each split parameter. Empty branches stay pending. The dropdown is disabled until Mission defines a mode and for connected LoadEnergy inputs.

When spacecraft modes exist, **Preview mode** selects one mode or **All modes** for verification and shared expression results. **All modes** shows common shared values normally and differing values as **By mode**, with mode values in the tooltip. Split rows retain their own mode results when the preview changes. Verification feedback lists each mode's result. The workbook checkbox passes when all modes pass. Preview selection leaves the saved expression and workbook verification unchanged.

The requirement list shows an unset variable's bare name in monospace, without its units. Numeric values with magnitude above 999 show no decimal places. Other values show four significant figures. Numeric values and their units use monospace in the requirement list and parameter results. Powers written with `^` or `**`, such as `m^2` or `s**(-2)`, appear as superscripts. Leave literal units out of requirement prose when using the Units column.

**Save requirement** applies the edit and triggers autosave. **Cancel** or Escape discards the pane's changes, including new parameters. Opening a different requirement asks before discarding a changed draft. Saving preserves edits made in other tables while the pane was open. Ctrl+Enter or Cmd+Enter saves. Existing parameter values and equation inputs stay accessible even when their names are absent from the text. Removing a marker preserves populated cells. Empty, unused names created during the current edit are discarded. Use `$$name$$` markers consistently in requirement text.

## Verification methods and Python analyses

The requirement pane has a compact **Verification methods** table with **Values from**, **Python condition** and **Result** columns. Its plus button focuses the trailing empty row. Entering a condition adds another empty row. Empty placeholders are excluded from saved data. Each requirement supports up to 32 configured methods. Every method must pass in every configured spacecraft mode for the workbook checkbox to pass. Missing inputs or execution results keep the affected method pending. Errors appear beside that method's condition.

**Requirement values** uses the current requirement's parameters and references such as `REQ002.mass`. Selecting a script instance keeps the condition in Python and supplies external outputs such as `SCR001.upper`. The selected script must have a successful execution for the current inputs, including when the condition is a constant. Script output references also work in ordinary parameter expressions and in other script instances' inputs.

### Use a Python script

1. Expand **Python scripts** inside the requirement pane. This section stays collapsed during ordinary requirement editing.
2. Choose a registered definition and click **Add script**. Each instance receives a stable key and an editable ID such as `SCR001`. Its expandable editor shows its input expressions and declared output references. Script parameters have their own names and types, separate from the workspace's shared requirement variables.
3. Bind its inputs using literals, local input names or references such as `REQ001.mass`. Mode conditions use Python syntax, such as `2 if mode == "Downlink" else 1`. Inputs start unset.
4. Select the instance in a verification method's **Values from** column and enter a condition such as `SCR001.upper <= REQ002.limit`. Boolean script outputs can be used directly in conditions.
5. Click **Run Python** to execute for every configured mode. Dependent scripts run first when their outputs are needed. The library shows input values, output values, execution times and diagnostics. **Preview mode** selects the displayed mode. Differing values show **By mode** when previewing all modes.

Definitions are reusable across instances and requirements in the workspace. ID renames update expression references. Remove expression and verification links before deleting an instance. Requirement **Save**, **Cancel** and **Save as** include script configuration edits. Concurrent changes to the same script or verification table produce a conflict. Saved JSON sessions retain each instance's interface, bindings and source revision.

Execution results stay in the current browser session. They are never stored as parameter expressions or verification flags. Changing calculation inputs, modes, types, units, script bindings or pinned revisions invalidates prior results. Prose and verification conditions can change without rerunning an unchanged calculation. Saving retains current evidence in that browser. Reloading or switching sessions requires another run. Late results from an earlier input configuration are discarded.

The default script directory is `framework/requirements-ui/scripts`. It includes **Normal distribution interval**, a Python standard library example with no supplied measurement data or confidence assumption. Python 3.8 or later is also required by the automatic calculation worker. Set `VERIFICATION_PYTHON` to select an interpreter or virtual environment. Set `VERIFICATION_SCRIPTS_DIR` to use another trusted directory. See [scripts/README.md](scripts/README.md) for registration, the JSON protocol and execution limits.

**Run only trusted local scripts. Python runs with your user permissions. This is not a sandbox.** Opening, editing, saving and exporting never execute registered script source. Automatic Python expressions use the restricted calculation worker. The browser can run registered script source only through an explicit local POST. It cannot submit source, file paths, shell commands or interpreter arguments.

JSON downloads contain each analysis's typed interface, input expressions and pinned definition revision. They contain no execution success flags or cached output bindings. Reopening a download requires fresh execution evidence before script-backed verification methods can pass.

## Reusable sizing requirements

`worker/catalog_data.py` owns the generic requirement definitions, Python equations and acceptance predicates. Its typed models supply table text, parameters, units, sources and assignments. Preloaded unit labels live in the Units column. Requirement prose uses variable markers without literal unit labels. Mission files contain typed usages and mission inputs. Editing a mission leaves these generic definitions unchanged.

The Generic EPS starter has 27 generic requirements. Mission has ORB001 through ORB003. EPS has SIZ001 through SIZ008, SIZ011, SIZ013, SIZ014, SIZ016, EPS002, EPS008, EPS009, EPS011, EPS019, EPS021, EPS047, EPS052, EPS053, EPS078, EPS088 and EPS089. Each requirement contains one sentence and at least one declared numeric parameter referenced in its text. Requirements without numeric parameters are excluded. IDs are preserved, so gaps are intentional. Separate obligations have their own rows, with **Source** links to the requirement they derive from. Python `derives_from` relationships supply these links. IDs can differ when an existing mission already uses them. Each new Power subsystem gets independent EPS inputs and local equation links.

Requirement text references named `$$variables$$`. Their definitions and equations appear in the parameter matrix. For example, SIZ007 references `$$battery_min_J$$`, whose expression is `eclipse_energy_J / dod_max * (1 + degradation_margin)`. Entering mission inputs evaluates the text and its dependent parameters without changing the generic definitions.

Populate these inputs in order:

1. **ORB001:** `altitude_km`. The sourced reference Earth constants are `earthRadius_km = 6378` and `gravitationalParameter_km3_s2 = 398601`. They remain editable. ORB001 and ORB002 derive the orbit, sunlight and eclipse periods in seconds.
2. **SIZ001:** Choose **Component modes** as its load input source, or enter `sunlight_power_W`, `eclipse_power_W`, `sunlight_duty` and `eclipse_duty` manually. Use disjoint load totals. Already duty-weighted totals use duty 1. The row derives energy in joules.
3. **SIZ002:** `sunlight_efficiency` and `eclipse_efficiency`, each in (0, 1]. The row derives minimum panel power in watts.
4. **SIZ003:** `cell_eol_V` and `cell_eol_A` from compatible EOL conditions. **SIZ004:** `installed_cells`. Required physical counts round upward.
5. **SIZ005:** `lifetime_years` and `days_per_year`. Orbits per day derive from the orbit period. The preliminary assumption is one nominal battery cycle per orbit.
6. **SIZ006:** sourced `cycle_a`, `cycle_b`, `fit_dod_min`, `fit_dod_max` and selected `dod_max`. The decreasing power-law fit requires `a > 0` and `b < 0`. The selected DoD must be inside its sourced fit domain and support the required cycles. No chemistry or fit coefficients are assumed.
7. **SIZ007:** `degradation_margin`. Minimum battery energy is `E_e / DoD * (1 + M)` in joules. **SIZ008:** `pack_bol_J` and applicable `retained_energy_factor`. Convert Wh to J by multiplying by 3600. Margin enters preliminary sizing once. Retained capacity is derived separately.

Every expression cell in the pane stores editable Python expression text. All catalog equations are Python. A literal such as `500` and an equation such as `2 * pi * sqrt(x)` use the same representation. The expression stays visible beside its evaluated value. You can edit or replace any prefilled equation. Editing a cell recalculates dependent values across tabs. Empty cells stay unset. Expressions that depend on empty cells show Pending. Syntax, reference, type and arithmetic errors appear in the affected cell with details in its tooltip. Insufficient cell counts, cycle life or capacity remain visible through the requirement conditions. Conditions also check that edited derived expressions still satisfy the generic sizing equations. Mission altitude, lifetime, duty cycles, efficiencies, selected products and margins have no default values. Existing free-text orbit statements are preserved. They do not silently supply sizing inputs.

These equations implement the preliminary circular orbit case in `final_report/design-proposal.tex`. They establish no seasonal illumination, peak-current, thermal or survival compliance. The retained EPS requirements cover generation, battery capacity and cycling, energy closure, mass, volume, memory and processor utilization. Each row retains its report source. Report criteria without defined numeric parameters remain in the report and are excluded from the workbook and generic requirement library. Complete scenario assessments remain unverified until applicable evidence and verification conditions are supplied. Python requirement models retain executable numerical and engineering acceptance predicates. Their `assess(values)` method accepts explicit numeric and Boolean evidence inputs. Missing evidence remains pending. These model assessments stay separate from the engineer's editable verification method table and supply no automatic compliance claim.

Click **Export workspace JSON** in the requirements table header to download the full current workspace, including valid unsaved inputs, expressions and provenance. Execution results stay transient. The download preserves expressions as data and establishes no verification or qualification claim.

## Tables

- Both ID columns are text fields. Stakeholder and domain element IDs have three uppercase letters, such as `LPR` or `ORB`. Statement IDs have three uppercase letters followed by three digits, such as `REQ001`. IDs are assigned automatically and remain editable.
- Enter stakeholders and choose Regulatory Agency, Mission Stakeholder, Launch Provider or Partner.
- External accepts requirements, needs, objectives, concerns and constraints. Its statement type dropdown is in the requirement editor. Other tabs list derived requirements.
- Dropdown cells use plain text and a small arrow at the right edge. Linked IDs are plain links with no pill background.
- **Source** links to individual rows anywhere in the workbook. Open the picker and check the rows to link. Click a linked ID to open its tab and focus that row. Source and assignment links survive ID changes. Source cycles are blocked across all tabs.
- Write `$$mass$$` in the pane's requirement text to add a parameter row. The list substitutes formatted values with units. Unset values show the variable name in monospace.
- Numeric expressions retain the model's declared types. Integer results must be safe JavaScript integers. Real results must be finite. Clearing an expression leaves the parameter unset.
- **Verified** shows a read-only checkbox and a pencil. Click the pencil or press F2 to open the requirement pane at its verification methods. The checkbox cannot be toggled manually. All configured methods must pass. A row without a verification method stays unverified. Enter `True` or `False` only when you intend an explicit constant Python condition.
- Each table starts with one empty placeholder row. Filling the last row adds a new placeholder. Empty placeholders are excluded from saved data.
- The **+** beside a table title inserts a row. Hover over a row to reveal its trash button in the left gutter. This deletes that row directly, regardless of selection. Remove its source and assignment links before deleting it. Rows with children remain protected.
- Tab moves between cells and their edit buttons. Enter moves down in ordinary fields. Enter, Space or F2 on requirement text opens its editor. Shift reverses navigation. Shift+Tab from an ID cell focuses that row's trash button. Enter activates it. Requirement text supports line breaks inside the pane.
- Headers use text labels. Click a column header to sort. Paste tab separated cells from Google Sheets in data column order, starting with ID. The delete gutter is separate from the data. Pasted sources and assignments accept comma separated row IDs or unique element names. Text and verification cells accept edits only through the pane. Grid pastes that would overwrite them are rejected as a whole. Paste a single column of expressions or units down the corresponding pane column, following its displayed state rows. Invalid expressions remain drafts and show cell errors.

## Parameter and verification expressions

Parameters accept numeric expressions without an assignment or leading `=`:

```python
12
1.2e3
mass * 2
REQ002.mass / 2
math.sqrt(x)
18 if mode == "Downlink" else 3
REQ002.mass * 1.2 if mode == "Nominal" else None
sum(i ** 2 for i in range(10))
statistics.mean([REQ001.mass, REQ002.mass])
```

Use a Boolean expression in each **Verification methods** row to check a requirement. Use the current row's variable names directly. Use another statement's ID and a variable name for a reference, including statements on other tabs. IDs are unique across the workbook:

```python
mass <= 2.5
mass <= NED001.mass and cell_count >= 3
not (x > 10) or y == 0
0 < x <= REQ002.x
all(i >= 0 for i in range(10))
math.isclose(x, REQ002.x, rel_tol=1e-6)
```

Supported syntax:

- Finite numeric literals, including scientific notation.
- Variable names and `ROW001.variable` references.
- Parentheses and unary `+`, `-`, `not`.
- Arithmetic `+`, `-`, `*`, `/`, `//`, `%` and `**` (power).
- Comparisons `<`, `<=`, `>`, `>=`, `==`, `!=`, including chained comparisons.
- Boolean literals `True`, `False` and operators `and`, `or`, `not`. Boolean operators and conditions require Boolean operands.
- Conditional expressions `value if condition else alternative`, including nested conditions. The built-in `mode` input compares with a quoted spacecraft mode name. Only the selected branch is evaluated. All branches are checked for syntax, references and compatible types. A selected `None` branch remains pending.
- Numeric functions `sqrt`, `acos`, `arccos`, `floor`, `ceil`, `abs`, `round`, `exp`, `log`, `log10`, `sin`, `cos`, `tan`, `hypot`, `min` and `max`. Use the `math.` prefix for Python math module functions, such as `math.sqrt` and `math.acos`. Built-ins such as `abs` and `round` use their bare names. Constants include `pi`, `math.pi`, `math.e` and `math.tau`. Trigonometric arguments and results use radians.
- Lists, tuples, `sum`, `len`, bounded `range`, and a single comprehension generator with optional Boolean filters. `all` and `any` consume Boolean collections. Comprehension variables have their own local names and cannot shadow module, function, row-ID or mode names. Collections and ranges contain at most 1,024 items.
- `statistics.mean`, `statistics.median`, `statistics.stdev` and `statistics.pstdev`. `math.isclose` accepts `rel_tol` and `abs_tol`. `math.isfinite` returns a Boolean.

This is a restricted native Python expression evaluator. It parses Python with `ast` and evaluates explicitly permitted nodes and functions. It uses no `eval` or `exec`. Imports, assignment, arbitrary calls, object introspection, private attributes and unbounded collections are unavailable. Put comments in the rationale field. Registered scripts provide the explicit trusted execution path for unrestricted Python and installed packages.

Expressions contain at most 5,000 characters, 2,048 AST nodes and 64 nesting levels. Dependency depth is limited to 64 and each calculation request has an operation budget. Numeric results stay finite. The import adapter converts old SysML conditional syntax, Boolean spellings, qualified math calls and `^` powers once. Canonical JSON workspaces use Python directly. Write `**` for powers. A newly entered `^` is rejected by the restricted evaluator and is never silently treated as a power.

Parameter expressions must produce numbers of their model's declared type. Conditions must produce a Boolean. Parameters are evaluated even when the row has no verification condition. An unset dependency gives a pending result. Cycles, invalid syntax, unknown references, invalid result types and nonfinite arithmetic give an error. A parameter error appears beside its expression. Pending and error conditions use an indeterminate checkbox with details in its tooltip. Results recalculate when expressions change, including references to other rows.

Expression references use visible row IDs. Renaming an ID through the UI updates condition and equation references. Renaming a spacecraft mode updates its quoted expression references. Remove these references before deleting a mode. Deleting an unused mode preserves the requirement rows. Source links use stable internal keys and remain intact.

## JSON storage

Edits autosave to the selected JSON workspace without a success toast. The footer reports saves and errors. Files contain the workspace object directly, with no generated code or wrapper. Expressions, stable keys, visible IDs, source links, allocations, states, units, rationale and script configuration are retained. Execution evidence and calculated values are never stored in their place.

JSON files are authoritative. An invalid or unsupported JSON file produces an error and is never replaced by a template. Writes use a temporary file, a filesystem sync and atomic publication. Existing workspace permissions are retained. Revision tokens include both file identity and contents, so a revision from another session cannot authorize a save. Queues and per-file `.lock` files protect concurrent saves across browser tabs, store instances and server processes. New JSON files are published with create-only semantics. Concurrent writers cannot replace another writer's new file.

After an interrupted server, a stale `.json.lock` may remain. Stop or confirm the owning server is no longer running before removing that lock. The lock contains its process ID and creation time. Never remove an active server's lock. Stale revisions and external edits keep local drafts open for recovery. Reload to use the current file, or use **Save as** to preserve a separate valid draft.

The stored mission and saved sessions are already version 14 JSON with Python expressions. Older versions, wrapped model files and non-Python expression formats are rejected. Reading a workspace performs no migration, reseeding or expression rewriting.

The maintained catalog is Python code and is trusted application configuration. It retains requirement text, units, parameter order, derivation links, declared attributes and acceptance predicates. JavaScript handles presentation, structural editing and JSON transport. Python is the sole calculation engine, including verification state carried into KiCad downloads.

## Test

```sh
npm test
```

No SysML compiler, renderer or model library is required for the app or its test suite.

Tests use temporary files and leave project models unchanged. Optional browser tests exercise the pane, sessions, saved copies, autosave isolation, workbook navigation, cancellation, generated columns, evaluation, persistence and download:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs npm test
```
