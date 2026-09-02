# Protocol for a Systematic Review and Evidence Map of Model-Based Systems Engineering for Nanosatellite Electrical Power Systems — Discovery and screening

## Information sources

- **Scopus:** bibliographic database.
- **Web of Science Core Collection:** bibliographic and citation database on the Clarivate Web of Science platform.
- **IEEE Xplore:** bibliographic and full-text database.
- **arXiv:** the full multidisciplinary preprint repository.
- **Compendex** and **Inspec:** search these together through Engineering Village, but keep their records and counts separate.
- **Wiley Online Library:** the full publisher platform.
- **Springer Nature Link:** the full publisher platform.
- **Advanced Technologies & Aerospace Index:** select only this index on the ProQuest Platform.
- **ProQuest Dissertations & Theses Global (PQDT Global):** select only this database on the ProQuest Platform, in a separate search event.
- **AIAA Aerospace Research Central (ARC):** the full publisher-hosted collection.
- **IAF Digital Library:** the full database.
- **Open Access Theses and Dissertations (OATD):** the full public index of electronic theses and dissertations.
- **ESA Indico:** the full public event and contribution database.
- **NASA Technical Reports Server (NTRS):** the full public technical-report database.

For PRISMA-S, name PQDT Global as a database on the ProQuest Platform and describe OATD as an indexed online resource. For the PRISMA 2020 flow diagram, count OATD under websites and other methods. OATD is still a required source and keeps its own total.

## Search strategy

### Search streams and set construction

Use two complementary streams because an EPS thread inside a wider spacecraft model may not appear in bibliographic metadata.

- **Stream A — EPS-explicit:** Population × EPS × MBSE/system-model concepts.
- **Stream B — embedded-thread recall:** Population × MBSE/system-model concepts and conservative artifact or tailoring expansions, without requiring an EPS term. Every Stream B candidate must be checked at full text for an eligible EPS thread.

The 13 direct query families are Scopus, Web of Science Core Collection, IEEE Xplore, Engineering Village, Wiley Online Library, Springer Nature Link, Advanced Technologies & Aerospace Index, PQDT Global, OATD, AIAA ARC, IAF Digital Library, NASA Technical Reports Server (NTRS), and arXiv. Engineering Village covers two databases, Compendex and Inspec.

#### Population and EPS blocks

- **Population (`P`):** `CubeSat`, `CubeSats`, `cube sat`, `cube sats`, `cube-sat`, `cube-sats`, `cube satellite`, `cube satellites`, `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites`, `nano-sat`, `nano-sats`, `nano sat`, `nano sats`, `nano-satellite`, `nano-satellites`, `nano satellite`, and `nano satellites`, `SmallSat`, `SmallSats`, `small satellite`, `small satellites`, `small sat`, and `small sats`.
- **High-specificity EPS (`E_H`):** `electrical power system`, `electrical power systems`, `electric power system`, `electric power systems`, `electrical power subsystem`, `electrical power subsystems`, `electric power subsystem`, `electric power subsystems`, `electrical energy subsystem`, `electrical energy subsystems`, `EPS`, `EPSs`, `power subsystem`, `power subsystems`, `power system`, `power systems`, `spacecraft power system`, `spacecraft power systems`, `power supply`, `power supplies`, `power distribution unit`, `power distribution units`, `PDU`, `PDUs`, `power processing unit`, `power processing units`, `power control and distribution`, `power management and distribution`, `electrical architecture`, `electrical architectures`, `power architecture`, `power architectures`, `DC power bus`, `DC power buses`, `PCDU`, `PCDUs`, `PMAD`, and `PMADs`.
- **Functional or analytical EPS (`E_F`):** `power budget`, `power budgets`, `energy budget`, `energy budgets`, `energy balance`, `energy balances`, `power balance`, `power balances`, `power margin`, `power margins`, `power generation`, `photovoltaic generator`, `photovoltaic generators`, `solar array`, `solar arrays`, `solar panel`, `solar panels`, `battery`, `batteries`, `battery management`, `state of charge`, `states of charge`, `energy storage`, `power electronics`, `power conditioning`, `power distribution`, `power management`, `power interface`, `power interfaces`, `power mode`, `power modes`, `load profile`, `load profiles`, `power consumption`, `power demand`, `power profile`, and `energy harvesting`.
- **All EPS (`E`):** `E_H ∪ E_F`.

#### MBSE and relationship blocks

- **High-specificity MBSE (`M_H`):** `model-based systems engineering`, `model based systems engineering`, `model-based system engineering`, `model based system engineering`, `model-driven systems engineering`, `model driven systems engineering`, `model-driven system engineering`, `model driven system engineering`, `model-centric systems engineering`, `model centric systems engineering`, `model-centric system engineering`, `model centric system engineering`, `MBSE`, `SysML`, `systems modeling language`, `systems modelling language`, `system modeling language`, `system modelling language`, `object-process methodology`, `object process methodology`, `OPM`, `object-oriented systems engineering method`, `object oriented systems engineering method`, `OOSEM`, `object-oriented systems engineering`, `object oriented systems engineering`, `Arcadia`, `Capella`, `model-based engineering`, `model based engineering`, `model-driven engineering`, `model driven engineering`, `model-based design`, `model based design`, `model-driven design`, `model driven design`, `MBE`, `MDE`, `MBD`, `MagicGrid`, `Harmony-SE`, `Harmony SE`, `RFLP`, `Cameo Systems Modeler`, `MagicDraw`, `IBM Engineering Systems Design Rhapsody`, `Rational Rhapsody`, `Vitech CORE`, `Vitech GENESYS`, `OpenMBEE`, `Enterprise Architect`, `MATLAB System Composer`, `System Composer`, and `Modelio`.
- **Broad structured model (`M_B`):** `system model`, `systems model`, `system modeling`, `systems modeling`, `system modelling`, `systems modelling`, `reference model`, `reference models`, `digital engineering`, `object-oriented systems model`, `object-oriented systems models`, `model-based system design`, `model based system design`, `model-based systems design`, `model based systems design`, `system architecture model`, `system architecture models`, `systems architecture model`, `systems architecture models`, `integrated system model`, `integrated system models`, `integrated systems model`, `integrated systems models`, `system-level model`, `system-level models`, `system level model`, `system level models`, `digital thread`, `digital threads`, `digital twin`, and `digital twins`.
- **All MBSE/system-model terms (`M`):** `M_H ∪ M_B`.
- **Systems-engineering relationship or concern (`R`):** `requirement`, `requirements`, `function`, `functions`, `functional`, `behavior`, `behaviors`, `behaviour`, `behaviours`, `behavioral`, `behavioural`, `architecture`, `architectures`, `architectural`, `interface`, `interfaces`, `traceability`, `trace`, `traceable`, `traced`, `allocation`, `allocate`, `allocated`, `constraint`, `constraints`, `parametric`, `parametrics`, `analysis`, `analyses`, `design`, `designs`, `designed`, `designing`, `decision`, `decisions`, `decision-making`, `decision making`, `trade study`, `trade studies`, `trade-off`, `trade-offs`, `tradeoff`, `tradeoffs`, `verification`, `verifications`, `verify`, `verifies`, `verified`, `verifying`, `validation`, `validations`, `validate`, `validates`, `validated`, and `validating`.

`M_B` requires `R` in direct B2 queries because its terms are otherwise broad. Stream A does not require `R`: the EPS block supplies the additional precision.

#### Artifact and tailoring blocks

Every term below is an ordinary token or ordered phrase. Compound definitions use only `AND` and `OR`.

- **Fixed precise reusable model or template (`G_model_fixed`):** `generic model`, `generic models`, `generic system model`, `generic system models`, `reusable model`, `reusable models`, `reusable system model`, `reusable system models`, `configurable model`, `configurable models`, `configurable system model`, `configurable system models`, `model template`, and `model templates`.
- **Mission-independence marker (`G_mission`):** `mission-agnostic`, `mission agnostic`, `mission-independent`, and `mission independent`.
- **Exact mission-independent artifact (`G_mission_exact`):** `mission-agnostic model`, `mission-agnostic models`, `mission-agnostic architecture`, `mission-agnostic architectures`, `mission agnostic model`, `mission agnostic models`, `mission agnostic architecture`, `mission agnostic architectures`, `mission-independent model`, `mission-independent models`, `mission-independent architecture`, `mission-independent architectures`, `mission independent model`, `mission independent models`, `mission independent architecture`, and `mission independent architectures`.
- **Precise reusable model or template (`G_model`):** `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`.
- **Fixed structural reusable artifact (`G_structure_fixed`):** `reference architecture`, `reference architectures`, `domain model`, `domain models`, `metamodel`, `metamodels`, `meta-model`, and `meta-models`.
- **Product-line or product-family marker (`G_product`):** `product-line`, `product line`, `product-family`, and `product family`.
- **Exact product model (`G_product_exact`):** `product-line model`, `product-line models`, `product line model`, `product line models`, `product-family model`, `product-family models`, `product family model`, and `product family models`.
- **Variation marker (`G_variation`):** `variation point` and `variation points`.
- **Structural reusable artifact (`G_structure`):** `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`.
- **Fixed conservative central asset (`C1_fixed`):** `reference model`, `reference models`, `system reference model`, `system reference models`, `model library`, `model libraries`, `system model library`, `system model libraries`, `model pattern`, `model patterns`, `modeling pattern`, `modeling patterns`, `modelling pattern`, `modelling patterns`, `system model pattern`, `system model patterns`, `systems model pattern`, `systems model patterns`, `model profile`, `model profiles`, `system model profile`, `system model profiles`, `systems model profile`, `systems model profiles`, `SysML profile`, and `SysML profiles`.
- **Domain-specific modeling-language marker (`G_DSL`):** `domain-specific modeling language`, `domain specific modeling language`, `domain-specific modelling language`, and `domain specific modelling language`.
- **Conservative central asset (`C1`):** `C1_fixed OR G_DSL`. Bare `library`, `pattern`, `profile`, or `language` never qualifies.
- **Precise tailoring (`T_precise`):** `tailor`, `tailors`, `tailored`, `tailoring`, `customize`, `customizes`, `customized`, `customizing`, `customization`, `customise`, `customises`, `customised`, `customising`, `customisation`, `parameterize`, `parameterizes`, `parameterized`, `parameterizing`, `parameterization`, `parameterise`, `parameterises`, `parameterised`, `parameterising`, `parameterisation`, `instantiate`, `instantiates`, `instantiated`, `instantiating`, `instantiation`, `variability`, `variation point`, and `variation points`.

The `M_B` context clauses limit noise from standalone mission and product markers. `B1` independently retrieves records that contain `P` and `M_H`.

`G_model`, `G_structure`, C1, and `T_precise` are recall concepts, not eligibility tests or evidence of reuse. An `architecture` occurrence inside an artifact phrase cannot also satisfy an independent R tag through the same text span.

#### Direct query schedule

Execute these nine semantic partitions in every direct query family unless a newly documented source limitation makes an exact translation impossible. A source may implement one semantic partition as a prospectively documented, lossless union of source-native query cells when a fixed query-length limit prevents one expression; preserve each cell's query, total, and stable identifiers and reconcile their union. A source-specific failure does not authorize an unrecorded narrower query.

| ID | Boolean form | Role |
|---|---|---|
| `A1` | `P AND E_H AND M_H` | Named EPS × explicit MBSE |
| `A2` | `P AND E_F AND (M_H OR M_B)` | EPS functions or analyses × all model terms |
| `A3` | `P AND E_H AND M_B` | Named EPS × broad structured model |
| `B1` | `P AND M_H` | Embedded-thread baseline |
| `B2` | `P AND M_B AND R` | Controlled broad-model expansion |
| `BG1` | `P AND G_model` | Precise reusable model or template |
| `BG2` | `P AND G_structure` | Structural reusable artifact |
| `BC1` | `P AND C1` | Conservative central asset |
| `BT2` | `P AND M_B AND T_precise` | Precise tailoring expansion |

Therefore:

- `Stream A = A1 ∪ A2 ∪ A3`;
- `core Stream B = B1 ∪ B2`; and
- `expanded Stream B = BG1 ∪ BG2 ∪ BC1 ∪ BT2`.

Retain and screen every record returned by any planned partition while preserving each discovery event. Report intersections and records unique to each stream and expansion after within-source and cross-source deduplication.

### Controlled vocabulary and indexed terms

Free-text searching remains mandatory. When a source provides a genuine controlled vocabulary or a distinct indexed-term field, construct the applicable concept as the union of its free-text block and validated source-specific descriptors. Inspect thesaurus scope notes, hierarchy, narrower terms, and terms assigned to known relevant records; use explosion only when every included narrower concept is in scope. A generic `systems engineering` descriptor cannot satisfy `M_H` by itself. Combine it with a model or modeling descriptor using Boolean `AND`, unless the source supplies a specific MBSE descriptor. Do not impose major-topic restrictions, and do not emulate controlled vocabulary on sources that do not provide it.

### New-run source translations and search artifacts

The source-specific guidelines will be recorded in `source-specific/`.
For PRISMA-S reporting, search rationales and strategies are linked to the cross-source query schedule and citation chasing strategy, so they are not source-specific.

### Finalizing searches and citation searches

Searches are finalized only after all 15 planned sources or collections have either a final run covering the entire source-specific schedule or a recorded final failure that excludes them from the review. Merge records only from complete successful events. Preserve separate Compendex and Inspec discovery instances and separate events for the two ProQuest sources.

Start backward and forward citation searching from every included full-text report and relevant secondary review:

- inspect each seed's complete reference list;
- search forward citations in both Scopus and Web of Science Core Collection;
- add each newly included report as a seed in the next numbered cycle; and
- stop only after one complete cycle of backward searching and both forward searches finds no new eligible report.

For every citation event, record the seed, platform, direction, cycle, source and retrieved totals, candidates, duplicates, decisions, failures, and stopping result. Use `discovery_route=citation_chasing`; citation provenance never bypasses screening.

Final searches are saved to `source-specific/*/final-searches/`, both for discovery and citation chasing (for Scopus and WoS only).

## Data management and audit trail

Make deduplication reproducible via a single `SLR/SLR1/deduplication.py`. Review conflicts manually when identifiers disagree. Keep both the original metadata and the preferred normalized value, with the reason for choosing it.

## Screening and eligibility procedure

### Title and abstract screening

- **Candidate:** the title or abstract clearly suggests EPS-primary MBSE or a likely embedded EPS thread, or the record appears to meet the nanosatellite and MBSE rules, but the abstract cannot confirm an embedded EPS thread.
- **Reject:** the record clearly has the wrong population, publication type, date, language, or is outside MBSE scope, or clearly has no qualifying EPS link.

Do not require an EPS or power term in a Stream B title or abstract. Embedded threads may be absent from metadata. If nanosatellite MBSE is plausible, retrieve the full text and resolve uncertainty there.

### Full-text decision

Assign exactly one final decision and give a source-located reason:

- `include_route_A_eps_primary`;
- `include_route_B_embedded_eps`;
- `exclude_no_qualifying_eps_thread`;
- `exclude_not_mbse`;
- `exclude_wrong_population`;
- `exclude_wrong_publication_type`;
- `exclude_wrong_date`;
- `exclude_wrong_language`;
- `exclude_secondary_study`;
- `not_retrieved`.

If thesis or dissertation completion status is unresolved, hold the record as `publication_type_unresolved` while looking for source-locatable clarification. If a record in the cutoff year gives only a year, or thesis dates conflict, hold it as `date_unresolved`. Do not silently turn either temporary status into an exclusion.

If a plausible completed report is unavailable because of access rights, an embargo, or a broken repository link, use `not_retrieved`. Do not call it the wrong publication type because it is unavailable.
