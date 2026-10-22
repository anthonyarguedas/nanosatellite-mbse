# Orbitwork KiCad architecture review

Review-only logical COTS interconnect drawing. Named sheet ports express proposed functional associations, not manufacturer terminals, electrical nets or an approved harness. No PCB, internal COTS circuit reconstruction, electrical compatibility, manufacturing or flight-readiness claim.

Open orbitwork-review.kicad_sch in KiCad. All child sheets must remain in the same directory. The project contains only hierarchical sheets, named logical ports and automatically drawn intent links. It deliberately contains no manufacturer symbol pins, footprints or PCB. An electrical netlist exported by KiCad will contain no physical components.

Product identities, exact catalog revisions, source URLs, quantities, accounting boundaries, role allocations, scenario data and missing physical-data gates are in manifest.json. Quantity does not specify an installed arrangement. One integrated board is represented by one usage sheet even when it supplies several roles. Internal role associations are recorded in the manifest and are not drawn as fake external wires.

The links are proposed functional associations derived from the role allocations. They are neither manufacturer wiring nor validated electrical connections. L_HOST_ALLOCATION is a logical software relation. L_STORAGE_PATH does not resolve charging direction, returns or isolation. No load channel mapping is invented.

Physical routing is blocked. Provide reviewed connector and return pin maps, exact footprints, supported installed configurations, an approved pin-level netlist, current and voltage constraints, board geometry and a configured router before physical design. Catalog ratings cannot reconstruct proprietary COTS circuits.

Local validation from the Orbitwork source checkout:

    node scripts/kicad-validate.mjs /path/to/unzipped-export

The validator retains raw KiCad SVG, netlist and ERC reports. Any zero ERC count concerns only these abstract sheets and establishes no electrical pass. Physical DRC is not run. The supplied workspace snapshot is for traceability, not permission to trust imported calculation caches.

Warnings:
- Review-only logical COTS interconnect drawing. Named sheet ports express proposed functional associations, not manufacturer terminals, electrical nets or an approved harness. No PCB, internal COTS circuit reconstruction, electrical compatibility, manufacturing or flight-readiness claim.
- Product hardware revisions that are unstated in the catalog remain unknown. Catalog record revisions are preserved verbatim.
- Candidate records do not bind a catalog revision. Reevaluate candidates after catalog changes. This export freezes the supplied catalog and selected entries.
- 3G30C-Advanced bare cell (8 × 8 cm): preliminary match is incomplete. priceUsd (no cost ranking) installed orientation, temperature/lifetime applicability and interconnection input tracking/open-circuit/current compatibility guaranteed EOL lower bound under applicable conditions cell assembly series/parallel arrangement, interconnects, bypass/blocking protection, packaging and installation evidence
- NanoPower BP8 100 Wh (8S1P): preliminary match is incomplete. priceUsd (no cost ranking) sourced retained energy/charge and applicable temperature/lifetime bounds charger policy, voltage mapping and installed interfaces conservative sourced BOL energy rating cycleLife
- NanoPower P80 (configuration 1): preliminary match is incomplete. priceUsd (no cost ranking) installed array voltage/current extrema and channel allocation conversion/startup envelope and charger compatibility inputMinV: missing or not applicable maxInputW: missing or not applicable guaranteed maxInputW limit or source input
- Unallocated roles: software. No COTS hardware is invented for these roles.
