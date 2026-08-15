# CUBICS 2022 CubeSat knowledge graph

This directory contains a source-aware, interactive graph of the nine Canadian Space Agency (CSA) **CUBICS 2022** grants. The opportunity was posted in September 2022 and CSA announced the nine awards in June 2023.

## Files

- `ontology.py` — node and edge types for grants, CubeSats, objectives, payloads, collaborators, partners, facilities, status and aliases.
- `cubics_2022_graph.py` — curated data, semantic validation and PyVis renderer.
- `cubics_2022_knowledge_graph.html` — generated, self-contained interactive graph and project dossier.
- `requirements.txt` — renderer dependency.

## View or regenerate

Open `cubics_2022_knowledge_graph.html` in a browser. Hover to read evidence and double-click a node or edge to open its source.

```bash
cd knowledge-graphs/cubics_2022
../canada_nanosatellites/.venv/bin/python cubics_2022_graph.py
```

The generated HTML uses nine disconnected recipient → CubeSat mini-graphs: CSA and CUBICS are retained as provenance in the dossier and sources, not as hub nodes in the visual graph. A gravity-based ForceAtlas layout with collision avoidance separates the components; use the **Focus a project** selector to isolate and fit any mini-graph. It uses only three node shapes (recipient box, CubeSat triangle, and color-coded fact dots), and displays every relation label on its edge. Flight status and source-recorded review, test, integration or commissioning milestones are annotations in the CubeSat hover note, not graph nodes. The source-linked dossier has one row per recipient and the requested fields: objectives, payloads, flight status, collaborators, partners and facilities.

## Scope and evidence rules

- The official roster, recipient names and grant values come from [CSA's CUBICS page](https://www.asc-csa.gc.ca/eng/satellites/cubics/about.asp), not from inferred project names in the broader Canadian-nanosatellite graph.
- Status assessment cutoff: **2026-08-15**. `Launched` is used only where a launch source was found; `Planned` means no launch confirmation was found in the reviewed public material.
- Every graph node and relation has a source URL. The HTML dossier exposes all field-level sources, including clearly labeled archived pages.
- A gray “public-evidence gap” is deliberate: it means a reviewed public page did not name the requested payload, partner or facility. It does not mean that capability does not exist.
- No NASA lifecycle phase is inferred or drawn as a node. If a project source objectively records reviews, tests, integration or commissioning, that evidence appears only in the CubeSat hover note; the note explicitly says when no NASA phase is published.
- `SKYA'ANA` / `SKYA'ANAsat` is represented as a former name of **MARMOTSat**, per the supplied clarification and historic CSA selection material; it is not a tenth recipient. `Killick-2` / `MUNStars-1` is likewise normalized to current **MUNStar-1**. The historic Manitoba label `IceCube` is linked to ArcticSat as a deliberately uncertain possible identity, not an asserted rename.

The graph intentionally distinguishes a team collaborator, a component/service partner, and a test/operations facility rather than collapsing them into a generic organization node.
