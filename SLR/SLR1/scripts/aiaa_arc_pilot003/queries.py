"""Exact literal ARC translations for Pilot 003 field-assignment cells.

Every term originates in protocol-discovery-and-appraisal.md.  Pairs use the
source's documented broader same-field fallback: ``("left" "right")``.
"""

from __future__ import annotations


def literal(value: str) -> str:
    return f'"{value}"'


def pair(left: str, right: str) -> str:
    return f"({literal(left)} {literal(right)})"


def block(literals: tuple[str, ...], pairs: tuple[tuple[str, str], ...] = ()) -> str:
    return "(" + " OR ".join([*(literal(value) for value in literals), *(pair(*value) for value in pairs)]) + ")"


def and_blocks(*values: str) -> str:
    return " AND ".join(values)


def or_blocks(*values: str) -> str:
    return "(" + " OR ".join(values) + ")"


P_TERMS = (
    "CubeSat", "CubeSats", "cube sat", "cube sats", "cube-sat", "cube-sats",
    "cube satellite", "cube satellites", "nanosat", "nanosats", "nanosatellite",
    "nanosatellites", "nano-sat", "nano-sats", "nano sat", "nano sats",
    "nano-satellite", "nano-satellites", "nano satellite", "nano satellites",
    "SmallSat", "SmallSats", "small satellite", "small satellites", "small sat",
    "small sats",
)

EH_TERMS = (
    "electrical power system", "electrical power systems", "electric power system",
    "electric power systems", "electrical power subsystem", "electrical power subsystems",
    "electric power subsystem", "electric power subsystems", "electrical energy subsystem",
    "electrical energy subsystems", "EPS", "EPSs", "power subsystem", "power subsystems",
    "power system", "power systems", "spacecraft power system", "spacecraft power systems",
    "power supply", "power supplies", "power distribution unit", "power distribution units",
    "PDU", "PDUs", "power processing unit", "power processing units",
    "power control and distribution", "power management and distribution",
    "electrical architecture", "electrical architectures", "power architecture",
    "power architectures", "DC power bus", "DC power buses", "PCDU", "PCDUs", "PMAD",
    "PMADs",
)

EF_TERMS = (
    "power budget", "power budgets", "energy budget", "energy budgets", "energy balance",
    "energy balances", "power balance", "power balances", "power margin", "power margins",
    "power generation", "photovoltaic generator", "photovoltaic generators", "solar array",
    "solar arrays", "solar panel", "solar panels", "battery", "batteries",
    "battery management", "state of charge", "states of charge", "energy storage",
    "power electronics", "power conditioning", "power distribution", "power management",
    "power interface", "power interfaces", "power mode", "power modes", "load profile",
    "load profiles", "power consumption", "power demand", "power profile", "energy harvesting",
)

MH_TERMS = (
    "model-based systems engineering", "model based systems engineering",
    "model-based system engineering", "model based system engineering",
    "model-driven systems engineering", "model driven systems engineering",
    "model-driven system engineering", "model driven system engineering",
    "model-centric systems engineering", "model centric systems engineering",
    "model-centric system engineering", "model centric system engineering", "MBSE", "SysML",
    "systems modeling language", "systems modelling language", "system modeling language",
    "system modelling language", "object-process methodology", "object process methodology", "OPM",
    "object-oriented systems engineering method", "object oriented systems engineering method",
    "OOSEM", "object-oriented systems engineering", "object oriented systems engineering",
    "Arcadia", "Capella", "model-based engineering", "model based engineering",
    "model-driven engineering", "model driven engineering", "model-based design", "model based design",
    "model-driven design", "model driven design", "MBE", "MDE", "MBD", "MagicGrid", "Harmony-SE",
    "Harmony SE", "RFLP", "Cameo Systems Modeler", "MagicDraw",
    "IBM Engineering Systems Design Rhapsody", "Rational Rhapsody", "Vitech CORE",
    "Vitech GENESYS", "OpenMBEE", "Enterprise Architect", "MATLAB System Composer",
    "System Composer", "Modelio",
)

MB_TERMS = (
    "system model", "systems model", "system modeling", "systems modeling", "system modelling",
    "systems modelling", "reference model", "reference models", "digital engineering",
    "object-oriented systems model", "object-oriented systems models", "model-based system design",
    "model based system design", "model-based systems design", "model based systems design",
    "system architecture model", "system architecture models", "systems architecture model",
    "systems architecture models", "integrated system model", "integrated system models",
    "integrated systems model", "integrated systems models", "system-level model", "system-level models",
    "system level model", "system level models", "digital thread", "digital threads", "digital twin",
    "digital twins",
)

R_TERMS = (
    "requirement", "requirements", "function", "functions", "functional", "behavior", "behaviors",
    "behaviour", "behaviours", "behavioral", "behavioural", "architecture", "architectures",
    "architectural", "interface", "interfaces", "traceability", "trace", "traceable", "traced",
    "allocation", "allocate", "allocated", "constraint", "constraints", "parametric", "parametrics",
    "analysis", "analyses", "design", "designs", "designed", "designing", "decision", "decisions",
    "decision-making", "decision making", "trade study", "trade studies", "trade-off", "trade-offs",
    "tradeoff", "tradeoffs", "verification", "verifications", "verify", "verifies", "verified",
    "verifying", "validation", "validations", "validate", "validates", "validated", "validating",
)

GMODEL_TERMS = (
    "generic model", "generic models", "generic system model", "generic system models",
    "reusable model", "reusable models", "reusable system model", "reusable system models",
    "configurable model", "configurable models", "configurable system model",
    "configurable system models", "model template", "model templates",
)
GMODEL_PAIR_LEFTS = ("mission-agnostic", "mission agnostic", "mission-independent", "mission independent")
MODEL_ARCHITECTURE_ANCHORS = ("model", "models", "architecture", "architectures")

GSTRUCTURE_TERMS = (
    "reference architecture", "reference architectures", "domain model", "domain models", "metamodel",
    "metamodels", "meta-model", "meta-models",
)
GSTRUCTURE_PRODUCT_LEFTS = ("product-line", "product line", "product-family", "product family")
GSTRUCTURE_VARIATION_LEFTS = ("variation point", "variation points")

C1_TERMS = (
    "reference model", "reference models", "system reference model", "system reference models",
    "model library", "model libraries", "system model library", "system model libraries", "model pattern",
    "model patterns", "modeling pattern", "modeling patterns", "modelling pattern", "modelling patterns",
    "system model pattern", "system model patterns", "systems model pattern", "systems model patterns",
    "model profile", "model profiles", "system model profile", "system model profiles", "systems model profile",
    "systems model profiles", "SysML profile", "SysML profiles",
)
C1_PAIR_LEFTS = (
    "domain-specific modeling language", "domain specific modeling language",
    "domain-specific modelling language", "domain specific modelling language",
)
C1_ANCHORS = (
    "model-based systems engineering", "model based systems engineering",
    "model-based system engineering", "model based system engineering", "MBSE", "SysML",
    "systems modeling language", "system model", "systems model",
)

T2_PAIR_LEFTS = (
    "reuse", "reuses", "reused", "reusable", "reusing", "tailor", "tailors", "tailored",
    "tailoring", "customize", "customizes", "customized", "customizing", "customization", "customise",
    "customises", "customised", "customising", "customisation", "configure", "configures", "configured",
    "configuring", "configuration", "parameterize", "parameterizes", "parameterized", "parameterizing",
    "parameterization", "parameterise", "parameterises", "parameterised", "parameterising",
    "parameterisation", "instantiate", "instantiates", "instantiated", "instantiating", "instantiation",
    "variability", "variation point", "specialize", "specializes", "specialized", "specializing",
    "specialization", "specialise", "specialises", "specialised", "specialising", "specialisation", "adapt",
    "adapts", "adapted", "adapting", "adaptation",
)
T2_PAIRS = tuple(
    (left, right) for left in T2_PAIR_LEFTS for right in MODEL_ARCHITECTURE_ANCHORS
)
# Four named, disjoint OR subcells; concatenating them in this order restores T2.
T2_SUBBLOCKS = tuple(block((), T2_PAIRS[index:index + 56]) for index in range(0, len(T2_PAIRS), 56))

BLOCKS = {
    "P": block(P_TERMS),
    "E_H": block(EH_TERMS),
    "E_F": block(EF_TERMS),
    "M_H": block(MH_TERMS),
    "M_B": block(MB_TERMS),
    "R": block(R_TERMS),
    "G_model": block(
        GMODEL_TERMS,
        tuple((left, right) for left in GMODEL_PAIR_LEFTS for right in MODEL_ARCHITECTURE_ANCHORS),
    ),
    "G_structure": block(
        GSTRUCTURE_TERMS,
        tuple((left, right) for left in GSTRUCTURE_PRODUCT_LEFTS for right in ("model", "models"))
        + tuple((left, right) for left in GSTRUCTURE_VARIATION_LEFTS for right in MODEL_ARCHITECTURE_ANCHORS),
    ),
    "C1": block(
        C1_TERMS,
        tuple((left, right) for left in C1_PAIR_LEFTS for right in C1_ANCHORS),
    ),
    "T2": block((), T2_PAIRS),
}

M_ANY = or_blocks(BLOCKS["M_H"], BLOCKS["M_B"])

SCHEDULE = {
    "A1": {"remainder": and_blocks(BLOCKS["E_H"], BLOCKS["M_H"]), "defining": BLOCKS["M_H"], "defining_name": "M_H", "third": BLOCKS["E_H"], "third_name": "E_H"},
    "A2": {"remainder": and_blocks(BLOCKS["E_F"], M_ANY), "defining": M_ANY, "defining_name": "M_H_OR_M_B", "third": BLOCKS["E_F"], "third_name": "E_F"},
    "A3": {"remainder": and_blocks(BLOCKS["E_H"], BLOCKS["M_B"]), "defining": BLOCKS["M_B"], "defining_name": "M_B", "third": BLOCKS["E_H"], "third_name": "E_H"},
    "B1": {"remainder": BLOCKS["M_H"], "defining": BLOCKS["M_H"], "defining_name": "M_H", "third": None, "third_name": None},
    "B2": {"remainder": and_blocks(BLOCKS["M_B"], BLOCKS["R"]), "defining": BLOCKS["M_B"], "defining_name": "M_B", "third": BLOCKS["R"], "third_name": "R"},
    "BG1": {"remainder": BLOCKS["G_model"], "defining": BLOCKS["G_model"], "defining_name": "G_model", "third": None, "third_name": None},
    "BG2": {"remainder": BLOCKS["G_structure"], "defining": BLOCKS["G_structure"], "defining_name": "G_structure", "third": None, "third_name": None},
    "BC1": {"remainder": BLOCKS["C1"], "defining": BLOCKS["C1"], "defining_name": "C1", "third": None, "third_name": None},
    "BT2": {"remainder": and_blocks(BLOCKS["M_B"], BLOCKS["T2"]), "defining": BLOCKS["M_B"], "defining_name": "M_B", "third": BLOCKS["T2"], "third_name": "T2"},
}

SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
METADATA_FIELDS = ("Title", "Keyword", "Abstract")


def first_stage_rows(schedule_id: str, population_field: str) -> tuple[tuple[str, str], ...]:
    entry = SCHEDULE[schedule_id]
    return ((population_field, BLOCKS["P"]), ("Anywhere", entry["remainder"]))


def refinement_rows(
    schedule_id: str, population_field: str, defining_field: str
) -> tuple[tuple[str, str], ...]:
    entry = SCHEDULE[schedule_id]
    rows: list[tuple[str, str]] = [
        (population_field, BLOCKS["P"]),
        (defining_field, entry["defining"]),
    ]
    if entry["third"] is not None:
        rows.append(("Anywhere", entry["third"]))
    return tuple(rows)


def semantic_query(schedule_id: str) -> str:
    return and_blocks(BLOCKS["P"], SCHEDULE[schedule_id]["remainder"])


assert len(P_TERMS) == 26
assert len(EH_TERMS) == 38
assert len(EF_TERMS) == 37
assert len(MH_TERMS) == 54
assert len(MB_TERMS) == 31
assert len(R_TERMS) == 55
assert len(GMODEL_TERMS) == 14 and len(GMODEL_PAIR_LEFTS) * len(MODEL_ARCHITECTURE_ANCHORS) == 16
assert len(GSTRUCTURE_TERMS) == 8 and 4 * 2 + 2 * 4 == 16
assert len(C1_TERMS) == 26 and len(C1_PAIR_LEFTS) * len(C1_ANCHORS) == 36
assert len(T2_PAIR_LEFTS) == 56 and len(T2_PAIRS) == 224
assert len(T2_SUBBLOCKS) == 4 and all(subblock.count(" OR ") + 1 == 56 for subblock in T2_SUBBLOCKS)
assert all("*" not in value and "?" not in value for value in BLOCKS.values())
