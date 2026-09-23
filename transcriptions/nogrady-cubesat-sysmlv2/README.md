# Nogrady CubeSat model in SysML v2

This directory contains a SysML v2 transcription of the Papyrus model from Sean Nogrady's thesis repository. The [official CSRM XMI transcription](../official-csrm-sysmlv2/README.md) uses the OMG and INCOSE distribution directly.

Source commit: `3fcde82462dd4988601262ae490a490df2c03281`

Source model:

https://github.com/snogrady/NogradyThesis_CubeSatConceptualDesignTool/tree/main/cubesatModel

## Contents

- `cubesatModel.sysml` contains the semantic transcription.
- `cubesatmodel-structure.svg` and `.png` are native Syside Modeler output for `CubeSat Domain`.
- `cubesatmodel-structure.manifest.json` records the native render provenance.
- `visualizations/model-package/` shows the top-level package organization.
- `visualizations/architecture-package/` shows the architecture package hierarchy.
- `visualizations/csm-elements/` shows the CSM element definitions and typed references.
- `visualizations/power-parameters/` shows the complete power parameter block.
- `visualizations/external-constraint-association/` shows one translated connection definition.

All listed images are native Syside Modeler exports. Each visualization directory includes its provenance manifest.

The transcription preserves 81 UML packages, 39 block classes, 2 actors, 1 use case, 1 activity, 13 value types, and 3 associations.

## Mapping

- SysML v1 Block becomes SysML v2 `part def`.
- SysML v1 ValueType becomes `attribute def`.
- UML actor becomes `part def`.
- UML use case becomes `use case def`.
- UML activity becomes `action def`.
- Block typed properties become `ref part` usages.
- UML associations become `connection def` elements.

The source XMI stores Power Parameters defaults as literal strings. The transcription preserves those values as `ScalarValues::String` and records each source value type in a comment. Papyrus diagram layout and Eclipse project metadata remain outside the semantic SysML source.

## Validation

Validated with Syside Modeler 0.10.3 through `~/agent-tools/sysmlv2`:

```sh
cd ~/agent-tools/sysmlv2
uv run skills/sysmlv2/scripts/model.py check \
  ~/nanosatellite-mbse/transcriptions/nogrady-cubesat-sysmlv2/cubesatModel.sysml \
  --json
```

The model passed parsing and semantic validation. Native structure rendering also passed.
