# ÉTS and McGill AIT institutional domains

These **native Syside tree diagrams** show published staff affiliations, roles, locations, and equipment. Each institution has its own diagram. They are selective organigrams of resources relevant to assembly, integration, and testing (AIT), not mission plans or inventories of confirmed CubeSat test capacity. Sources were checked on 23 September 2026.

A `ref part` connects a person to the unit that lists them. It does not treat a person as owned equipment. Every named person has a `position` attribute taken from the cited staff page. Their `potentialConcerns` attribute lists topics they **could** support, inferred from their published role or unit. The comma-separated topics are suggestions, not confirmed assignments. `potentialContact : Boolean = true` marks selected outreach candidates. It does not claim they agreed to work on CUBICS. The diagrams do not show unappointed leads or proposed partner agreements.

## ÉTS

![ÉTS AIT institutional tree](rendered/ets-tree/ets-ait-domain-structure.png)

[Native SVG](rendered/ets-tree/ets-ait-domain-structure.svg) · [SysML v2 source](ets-ait-domain.sysml)

| Unit shown under ÉTS | People shown at that unit | Equipment published by the unit |
| --- | --- | --- |
| Satellite and Space Research Center (CSSR) | Its **Our Team** page lists René Jr Landry as LASSENA director, Jean-Marc Gagné as LASSENA project manager, and Ahmad Esmailkhah as a postdoctoral fellow [1]. | CSSR reports vacuum chambers, space environment simulators, and radiation test devices [1]. |
| LaCIME | Ricardo Izquierdo is director. Mathieu Gratuze is a research associate. Mohsen Ketabi is a research assistant [2]. | Its equipment page lists vector network analyzers, a *pot vibrant* shaker, a TPS T10RC environmental chamber, and a vacuum test chamber [3]. |
| LTCC@ÉTS | Ammar B. Kouki is director. Normand Gravel is lab manager [4]. | The lab lists a P200S LTCC printer, Protolaser U3, PEO603 furnace, and 800MBA MEMS mask aligner [4]. |

The diagram places these three published units directly under the ÉTS domain. It does not infer a reporting line between CSSR, LaCIME, and LTCC@ÉTS. LaCIME mentions the LTCC laboratory in its contact and equipment pages [2, 3]. A listed chamber or shaker has no implied CubeSat test envelope or qualification status.

## McGill

![McGill AIT institutional tree](rendered/mcgill-tree/mcgill-ait-domain-structure.png)

[Native SVG](rendered/mcgill-tree/mcgill-ait-domain-structure.svg) · [SysML v2 source](mcgill-ait-domain.sysml)

| Unit shown under McGill | People shown at that unit | Equipment or location published by the unit |
| --- | --- | --- |
| Faculty of Engineering Workshop | Jamil Ahram is manager. Meisam Aghajani is a chief shop technician. Sam Minter is a coordinator at the Wong Machine Shop [5]. | Workshop Services lists CNC mills and lathes, a coordinate measuring machine, and a laser cutter [6]. |
| Nanotools Microfab | Zhao Lu is manager. John Li is equipment technologist. Peng Yang is research assistant [7]. | Nanotools lists ISO 5 and ISO 6 cleanrooms, lithography, thin film deposition, and etching. Its staff and cleanroom are in the Rutherford Physics Building basement [7, 8]. |

The McGill diagram treats the Workshop and Nanotools as separate published facilities. A cleanroom for microfabrication does not imply access to whole spacecraft assembly. Workshop jobs have a work order and funding approval process [6]. Nanotools has registration, supervisor approval, project review, and safety training requirements [9].

## Reproduce

Both `.sysml` models passed Syside Modeler 0.10.3 syntax and semantic validation with zero diagnostics. The native PNGs and SVGs were rendered using the parent [`syside.toml`](../syside.toml), which selects Syside's `tree` layout.

```sh
TOOL=/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py
CONFIG=cubics-2026-ets-mcgill/syside.toml
ETS=cubics-2026-ets-mcgill/ait/ets-ait-domain.sysml
MCGILL=cubics-2026-ets-mcgill/ait/mcgill-ait-domain.sysml
uv run "$TOOL" check "$ETS" --json
uv run "$TOOL" check "$MCGILL" --json
uv run "$TOOL" render "$ETS" --element "ETSAITDomain::'ÉTS AIT Institutional Domain'" --view structure --native-depth -1 --config "$CONFIG" --formats svg,png --output-dir cubics-2026-ets-mcgill/ait/rendered/ets-tree --json
uv run "$TOOL" render "$MCGILL" --element "McGillAITDomain::'McGill AIT Institutional Domain'" --view structure --native-depth -1 --config "$CONFIG" --formats svg,png --output-dir cubics-2026-ets-mcgill/ait/rendered/mcgill-tree --json
```

## Sources

1. [CSSR, equipment and team](https://cssr.etsmtl.ca/).
2. [ÉTS, LaCIME staff contacts](https://www.etsmtl.ca/laboratoires/lacime).
3. [ÉTS, LaCIME equipment](https://www.etsmtl.ca/laboratoires/lacime/equipement).
4. [ÉTS, LTCC@ÉTS staff and equipment](https://www.etsmtl.ca/recherche-innovation/chaires-laboratoires-instituts-centres/laboratoires-recherche/ltcc-ets).
5. [McGill, Faculty Workshop staff](https://www.mcgill.ca/engineering/faculty-staff/services-resources/faculty-workshop-services/team-members).
6. [McGill, Workshop Services](https://www.mcgill.ca/engineering/faculty-staff/services-resources/faculty-workshop-services/information-and-services/workshop-services).
7. [McGill, Nanotools staff and location](https://www.mcgill.ca/microfab/about/contact).
8. [McGill, Nanotools facility and equipment categories](https://www.mcgill.ca/microfab/about).
9. [McGill, Nanotools access process](https://www.mcgill.ca/microfab/getting-started-mcgill-nanotools).
