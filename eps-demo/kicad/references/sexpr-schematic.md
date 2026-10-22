---
url: "https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/"
final_url: "https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/"
title: "Schematic File Format | Developer Documentation | KiCad"
extracted_at: "2026-10-17T07:27:03.441324+00:00"
parser: "trafilatura-markdown"
confidence: 0.860
content_type: "text/html"
http_status: 200
word_count: 2098
---

# Schematic File Format

## Introduction

This documents the s-expression schematic file format for all versions of KiCad from 6.0.

-
Schematic files use the

`.kicad_sch`

extension.

### Instance Path

Because KiCad schematics can support multiple instances of the same schematic using hierarchical
sheets, information for shared sheets is done using paths consisting of the
[universally unique identifiers](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)
that represent the hierarchical path for the sheet the instance separated by a forward slash
('/'). A typical instance path would look like:

`"/00000000-0000-0000-0000-00004b3a13a4/00000000-0000-0000-0000-00004b617b88"`

|
The first identifier must be the root
|

### Label and Pin Shapes

The table below defines the valid shape tokens [global labels](https://dev-docs.kicad.org#_global_label_section),
[hierarchical labels](https://dev-docs.kicad.org#_hierarchical_label_section), and
[hierarchical sheet pins](https://dev-docs.kicad.org#_hierarchical_sheet_pin_definition).

| Token | Definition | Image |
|---|---|---|
input |
Label or pin is an input shape |
|
output |
Label or pin is an output shape |
|
bidirectional |
Label or pin is a bidirectional shape |
|
tri_state |
Label or pin is a tri-state shape |
|
passive |
Label or pin is a tri-state shape |

## Layout

A schematic file includes the following sections:

## Header Section

The `kicad_sch`

token indicates that it is KiCad schematic file. This section is required.

Third party scripts should not use `eeschema` as the generator identifier. Please use
some other identifier so that bugs introduced by third party generators are not confused
with a schematic file created by KiCad.
|

```
(kicad_sch
(version VERSION)
```**(1)**
(generator GENERATOR) **(2)**
;; contents of the schematic file... **(3)**
)

1 |
The `version` token attribute defines the schematic version using the YYYYMMDD date format. |
2 |
The `generator` token attribute defines the program used to write the file. |
3 |
The schematic sections go here. |

## Unique Identifier Section

The `uuid`

token defines the globally unique identifier that identifies the schematic.

` UNIQUE_IDENTIFIER `**(1)**

NOTE Only the root schematic identifier is used as the virtual root sheet identifier. All other
identifiers are belong to [hierarchical sheet objects](https://dev-docs.kicad.org#_hierarchical_sheet_section).

1 |
The UNIQUE_IDENTIFIER defines the
|

## Library Symbol Section

The `lib_symbols`

token defines a symbol library contain all of the symbols used in the
schematic.

```
(lib_symbols
SYMBOL_DEFINITIONS...
```**(1)**
)

1 |
A list of 0 or more
|

## Junction Section

The `junction`

token defines a junction in the schematic. The junction section will not exist
if there are no junctions in the schematic.

```
(junction
POSITION_IDENTIFIER
```**(1)**
(diameter DIAMETER) **(2)**
(color R G B A) **(3)**
UNIQUE_IDENTIFIER **(4)**
)

1 |
The POSITION_IDENTIFIER defines the
|

**2**`diameter`

token attribute defines the DIAMETER of the junction. A diameter of 0 is
the default diameter in the system settings.**3**`color`

token attributes define the Red, Green, Blue, and Alpha transparency of the
junction. If all four attributes are 0, the default junction color is used.**4**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the junction.## No Connect Section

The `no_connect`

token defines a unused pin connection in the schematic. The no connect section
will not exist if there are not any no connects in the schematic.

```
(no_connect
POSITION_IDENTIFIER
```**(1)**
UNIQUE_IDENTIFIER **(2)**
)

1 |
The POSITION_IDENTIFIER defines the
|

**2**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the no connect.## Bus Entry Section

The `bus_entry`

token defines a bus entry in the schematic. The bus entry section will not
exist if there are no bus entries in the schematic.

```
(bus_entry
POSITION_IDENTIFIER
```**(1)**
(size X Y) **(2)**
STROKE_DEFINITION **(3)**
UNIQUE_IDENTIFIER **(4)**
)

1 |
The POSITION_IDENTIFIER defines the
|

**2**`size`

token attributes define the X and Y distance of the end point from the position
of the bus entry.**3**[is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_stroke_definition).**4**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the bus entry.## Wire and Bus Section

The `wire`

and `bus`

tokens define wires and buses in the schematic. This section will not
exist if there are no wires or buses in the schematic.

```
(wire | bus
COORDINATE_POINT_LIST
```**(1)**
STROKE_DEFINITION **(2)**
UNIQUE_IDENTIFIER **(3)**
)

1 |
The COORDINATE_POINT_LIST defines the list of
|

**2**[is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_stroke_definition).**3**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the wire or bus.## Image Section

See common [Images](https://dev-docs.kicad.org/sexpr-intro/index.html#_images) section.

## Graphical Line Section

The `polyline`

token defines one or more lines that may or may not represent a polygon. This
section will not exist if there are no lines in the schematic.

```
(polyline
COORDINATE_POINT_LIST
```**(1)**
STROKE_DEFINITION **(2)**
UNIQUE_IDENTIFIER **(3)**
)

1 |
The COORDINATE_POINT_LIST defines the list of
|

**2**[is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_stroke_definition)..**3**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the graphical line.## Graphical Text Section

The `text`

token defines graphical text in a schematic.

```
(text
"TEXT"
```**(1)**
POSITION_IDENTIFIER **(2)**
TEXT_EFFECTS **(3)**
UNIQUE_IDENTIFIER **(4)**
)

1 |
The TEXT is a quoted string that defines the text. |
2 |
The POSITION_IDENTIFIER defines the
|

**3**[text is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_text_effects).**4**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the graphical text.## Local Label Section

The `label`

token defines an wire or bus label name in a schematic.

```
(label
"TEXT"
```**(1)**
POSITION_IDENTIFIER **(2)**
TEXT_EFFECTS **(3)**
UNIQUE_IDENTIFIER **(4)**
)

1 |
The TEXT is a quoted string that defines the label. |
2 |
The POSITION_IDENTIFIER defines the
|

**3**[label text is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_text_effects).**4**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the label.## Global Label Section

The `global_label`

token defines a label name that is visible across all schematics in
a design. This section will not exist if no global labels are defined in the schematic.

```
(global_label
"TEXT"
```**(1)**
(shape SHAPE) **(2)**
[(fields_autoplaced)] **(3)**
POSITION_IDENTIFIER **(4)**
TEXT_EFFECTS **(5)**
UNIQUE_IDENTIFIER **(6)**
PROPERTIES **(7)**
)

1 |
The TEXT is a quoted string that defines the global label. |
2 |
The `shape` token attribute defines the way the global label is drawn. See table below
for global label shapes. |
3 |
The optional `fields_autoplaced` is a flag that indicates that any PROPERTIES associated
with the global label have been place automatically. |
4 |
The POSITION_IDENTIFIER defines the
|

**5**[global label text is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_text_effects).**6**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the global label.**7**[properties](https://dev-docs.kicad.org/sexpr-intro/index.html#_symbol_property)of the global label. Currently, the only supported property is the inter-sheet reference.## Hierarchical Label Section

The `hierarchical_label`

section defines labels that are used by
[hierarchical sheets](https://dev-docs.kicad.org#_hierarchical_sheet_section) to define connections between sheet in
hierarchical designs. This section will not exist if no global labels are defined in the
schematic.

```
(hierarchical_label
"TEXT"
```**(1)**
(shape SHAPE) **(2)**
POSITION_IDENTIFIER **(3)**
TEXT_EFFECTS **(4)**
UNIQUE_IDENTIFIER **(5)**
)

1 |
The TEXT is a quoted string that defines the hierarchical label. |
2 |
The `shape` token attribute defines the way the hierarchical label is drawn. See table below
for hierarchical label shapes. |
3 |
The POSITION_IDENTIFIER defines the
|

**4**[hierarchical label text is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_text_effects).**5**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the hierarchical label.## Symbol Section

The `symbol`

token in the symbol section of the schematic defines an instance of a symbol from
[the library symbol section](https://dev-docs.kicad.org#_library_symbol_section) of the schematic.

```
(symbol
"LIBRARY_IDENTIFIER"
```**(1)**
POSITION_IDENTIFIER **(2)**
(unit UNIT) **(3)**
(in_bom yes|no) **(4)**
(on_board yes|no) **(5)**
UNIQUE_IDENTIFIER **(6)**
PROPERTIES **(7)**
(pin "1" (uuid e148648c-6605-4af1-832a-31eaf808c2f8)) **(8)**
(instances **(9)**
(project "PROJECT_NAME" **(10)**
(path "PATH_INSTANCE" **(11)**
(reference "REFERENCE") **(12)**
(unit UNIT) **(13)**
)
;; Optional symbol instances for this `project`...
)
;; Optional symbol instances for other `project`...
)
)

1 |
The
|

**2**[X and Y coordinates and angle of rotation](https://dev-docs.kicad.org/sexpr-intro/index.html#_position_identifier)of the symbol.**3**`unit`

token attribute defines which unit in the symbol library definition that the
schematic symbol represents.**4**`in_bom`

token attribute determines whether the schematic symbol appears in any bill of
materials output.**5**`on_board`

token attribute determines if the footprint associated with the symbol is
exported to the board via the netlist.**6**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the symbol. This is used to map the symbol the[symbol instance information](https://dev-docs.kicad.org#_symbol_instance_section).**7**[symbol properties](https://dev-docs.kicad.org/sexpr-intro/index.html#_symbol_property)of the schematic symbol.**8**`pin`

token attributes define ???.**9**`instances`

token defines a list of symbol instances grouped by project. Every symbol
will have a least one instance.**10**`project`

token attribute defines the name of the project to which the instance data
belongs. There can be instance data from other project when schematics are shared across
multiple projects. The projects will be sorted by the `PROJECT_NAME`

in alphabetical order.**11**`path`

token attribute is the [path to the sheet instance](https://dev-docs.kicad.org#_instance_path)for the instance data.**12**`reference`

token attribute is a string that defines the reference designator for the
symbol instance.**13**`unit`

token attribute is a integer ordinal that defines the symbol unit for the symbol
instance. For symbols that do not define multiple units, this will always be 1.## Hierarchical Sheet Section

The `sheet`

token defines a hierarchical sheet of the schematic.

```
(sheet
POSITION_IDENTIFIER
```**(1)**
(size WIDTH HEIGHT) **(2)**
[(fields_autoplaced)] **(3)**
STROKE_DEFINITION **(4)**
FILL_DEFINITION **(5)**
UNIQUE_IDENTIFIER **(6)**
SHEET_NAME_PROPERTY **(7)**
FILE_NAME_PROPERTY **(8)**
HIERARCHICAL_PINS **(9)**
(instances **(10)**
(project "PROJECT_NAME" **(11)**
(path "PATH_INSTANCE" **(12)**
(page "PAGE_NUMBER") **(13)**
)
;; Optional sheet instances for this `project`...
)
;; Optional sheet instances for other `project`...
)
)

1 |
The POSITION_IDENTIFIER defines the
|

**2**`size`

token attributes define the WIDTH and HEIGHT of the sheet.**3**`fields_autoplaced`

token indicates if the properties have been automatically
placed.**4**[outline is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_stroke_definition).**5**[filled](https://dev-docs.kicad.org/sexpr-intro/index.html#_fill_definition).**6**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the sheet. This is used to map the sheet[symbol instance information](https://dev-docs.kicad.org#_symbol_instance_section)and[sheet instance information](https://dev-docs.kicad.org#_hierarchical_sheet_instance_section).**7**[property](https://dev-docs.kicad.org/sexpr-intro/index.html#_symbol_property)that defines the name of the sheet. This property is mandatory.**8**[property](https://dev-docs.kicad.org/sexpr-intro/index.html#_symbol_property)that defines the file name of the sheet. This property is mandatory.**9**[hierarchical pins](https://dev-docs.kicad.org#_hierarchical_sheet_pin_definition)that map a[hierarchical label](https://dev-docs.kicad.org#_hierarchical_label_section)defined in the associated schematic file.**10**`instances`

token defines a list of sheet instances grouped by project. Every sheet
will have a least one instance.**11**`project`

token attribute defines the name of the project to which the instance data
belongs. There can be instance data from other project when schematics are shared across
multiple projects. The projects will be sorted by the `PROJECT_NAME`

in alphabetical order.**12**`path`

token attribute is the [path to the sheet instance](https://dev-docs.kicad.org#_instance_path)for the sheet instance data.**13**`page`

token attribute is a string that defines the page number for the sheet instance.### Hierarchical Sheet Pin Definition

The `pin`

token in a [sheet](https://dev-docs.kicad.org#_hierarchical_sheet_section) object defines an electrical connection
between the sheet in a schematic with the [hierarchical label](https://dev-docs.kicad.org#_hierarchical_label_section)
defined in the associated schematic file.

```
(pin
"NAME"
```**(1)**
input | output | bidirectional | tri_state | passive **(2)**
POSITION_IDENTIFIER **(3)**
TEXT_EFFECTS **(4)**
UNIQUE_IDENTIFIER **(5)**
)

1 |
The "NAME" attribute defines the name of the sheet pin. It must have an identically named
|

**2****3**[X and Y coordinates and angle of rotation](https://dev-docs.kicad.org/sexpr-intro/index.html#_position_identifier)of the pin in the sheet.**4**[pin name text is drawn](https://dev-docs.kicad.org/sexpr-intro/index.html#_text_effects).**5**[universally unique identifier](https://dev-docs.kicad.org/sexpr-intro/index.html#_universally_unique_identifier)for the pin.## Root Sheet Instance Section

```
(path
"/"
```**(1)**
(page "PAGE") **(2)**
)

1 |
The instance path is always empty ("/") since there are no sheets pointing to the root sheet. |
2 |
The `page` token defines the page number of the root sheet. Page numbers can be any valid
string. |
