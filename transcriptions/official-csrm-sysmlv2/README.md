# Official CSRM XMI in SysML v2

This is a source scoped transcription of the **official CubeSat System Reference Model (CSRM)**, independent of the Nogrady thesis model in `../nogrady-cubesat-sysmlv2/`.

## Sources and version

- Model authors: INCOSE Space Systems Working Group and OMG Space Domain Task Force. [Official CSRM repository](https://github.com/ObjectManagementGroup/CSRM), pinned at commit [`69c7f021fd1b2b0e9135dc9e6f926c12e514de7e`](https://github.com/ObjectManagementGroup/CSRM/tree/69c7f021fd1b2b0e9135dc9e6f926c12e514de7e).
- Model baseline: [`Distro/CSRM XMI/CSRM.xmi`](https://github.com/ObjectManagementGroup/CSRM/blob/69c7f021fd1b2b0e9135dc9e6f926c12e514de7e/Distro/CSRM%20XMI/CSRM.xmi), SHA-256 `52c48e735f1c497e1bcba5d152747b461c257c1cbe32391919dc196a3e32f99f`. This is the repository's **vendor-neutral distribution**, rather than a copy of Nogrady's Papyrus model.
- Profile baseline: [`Distro/CSRM XMI/23-11-16.xmi`](https://github.com/ObjectManagementGroup/CSRM/blob/69c7f021fd1b2b0e9135dc9e6f926c12e514de7e/Distro/CSRM%20XMI/23-11-16.xmi), SHA-256 `80e4156991ea3706de88fb2b2a61d6e70e723a2396852efdc441562fc19f31e6`.
- [OMG CSRM Profile v1.1](https://www.omg.org/spec/CSRM/1.1/PDF), particularly §1, identifies the GitHub template as a **non-normative example**. The OMG specification standardizes a SysML v1 profile. It does not publish a SysML v2 CSRM model.

The upstream README also advertises a **newer, temporary MDZIP release** under `DistroTemp/`, including a FireSat example. That proprietary tool distribution is a different revision. This transcription covers the pinned vendor-neutral XMI, **not** every subsequent release. The upstream distribution README explicitly says that the CSRM does not contain a complete satellite.

The CSRM repository states that its model is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The original XMI is retained in `source/` for attribution, trace checks, and details without direct SysML v2 equivalents.

## Files

| Path | Purpose |
| --- | --- |
| `CSRM.sysml` | Complete element inventory and semantic lowering of the pinned vendor-neutral model. |
| `CSRMProfile.sysml` | All 53 CSRM profile stereotype **names** represented as SysML v2 metadata definitions. This is not a replacement for the normative UML profile. |
| `source/` | Unchanged official model and profile XMI. |
| `source-map.json` | Every model XMI ID, its source attributes and applied stereotypes, and its target or documented owner. |
| `profile-map.json` | Profile stereotype names and source attributes, with profile XMI provenance. |
| `coverage.json` | Count by UML element kind and mapping scope. |
| `transcribe.py`, `transcribe_profile.py`, `test_transcription.py` | Deterministic generators and source coverage tests. |
| `visualizations/cubesat-domain/` | Native Syside structure render of the source CubeSat Domain definition, with provenance manifest. |

All **1,986 typed UML elements** with XMI IDs in `CSRM.xmi` occur in `CSRM.sysml` and have entries in `source-map.json`. This includes 255 packages, 335 classes, 47 activities, 6 use cases, 4 actors, 134 associations, 115 abstractions and dependencies, 277 properties, 66 activity parameter nodes, 22 control flows, 44 object flows, and 358 source comments. The source has two UML Models. `coverage.json` gives the entire inventory.

## Lowering and fidelity

- Packages and both UML models become nested SysML v2 packages. Stereotyped UML classes become `part def`, except requirement stereotypes, which become `requirement def`. The profile labels are applied as metadata. Source requirement `Text` becomes requirement documentation. Source IDs, other stereotype properties, and original comments are preserved.
- UML actors become part definitions. Use cases, activities, and actor operations become use case and action definitions. Activity nodes and pins become named action and item usages. Control flows become successions. Object flows become flows. Call behavior targets are represented by dependencies. UML abstractions and dependencies preserve their client to supplier direction as SysML dependencies, with original stereotype names and fields in documentation.
- Composite typed attributes become parts. Other typed attributes become reference parts. Source untyped properties become untyped attributes. Associations become connection definitions. The source end properties remain traceable in the source map.
- SysML v1 profile metaclass extensions, OCL constraints, UML diagram layout, partitions, event timing, and external MagicDraw generalization targets have **no asserted lossless SysML v2 equivalent** here. Their IDs and data are retained in documentation and the original XMI. Connector end multiplicity is preserved in the source map because SysML v2 connector ends require `[1..1]`. Unresolved source parameter types are recorded rather than invented.
- Some source requirements are placeholders such as “Shall statement,” and some have empty text. This transcription does not invent a mission-specific design or missing values.

Thus “complete” means **all semantic elements of this pinned model XMI are accounted for**, with explicit lowerings and source-only records. It does not mean behaviorally equivalent execution, a full translation of the OMG SysML v1 profile, a transcription of the newer temporary MDZIP release, or a fully populated satellite.

## Regenerate and validate

From the project root:

```sh
python3 transcriptions/official-csrm-sysmlv2/transcribe_profile.py
python3 transcriptions/official-csrm-sysmlv2/transcribe.py
python3 -m unittest discover -s transcriptions/official-csrm-sysmlv2 -p 'test_*.py' -v
cd ~/agent-tools
uv run sysmlv2/skills/sysmlv2/scripts/model.py check \
  ~/nanosatellite-mbse/transcriptions/official-csrm-sysmlv2 --json
```

The two SysML files passed Syside Modeler 0.10.3 parsing and semantic validation with zero diagnostics. A native structure render also passed. Run `check` on the directory so the profile metadata definitions are included.
