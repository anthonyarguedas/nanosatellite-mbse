"""Canonical AIAA ARC queries for the post-proximity Pilot 005.

The concept membership and compound Boolean definitions come from
protocol-discovery-and-appraisal.md at commit
3194156e90497186664260a8e86435e78d2e2aa1. Every source atom is one quoted
literal in ARC's Anywhere field. No proximity, pair expansion, or wildcard is
used.
"""

from __future__ import annotations

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CHANGED_IDS = ("BG1", "BG2", "BC1", "BT2")


def literal(value: str) -> str:
    return f'"{value}"'


def ordinary_block(terms: tuple[str, ...]) -> str:
    if not terms:
        raise ValueError("An ordinary block requires at least one term")
    return "(" + " OR ".join(literal(term) for term in terms) + ")"


def any_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("OR requires at least one expression")
    return "(" + " OR ".join(expressions) + ")"


def all_of(*expressions: str) -> str:
    if not expressions:
        raise ValueError("AND requires at least one expression")
    return "(" + " AND ".join(expressions) + ")"


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

GMODEL_FIXED_TERMS = (
    "generic model", "generic models", "generic system model", "generic system models",
    "reusable model", "reusable models", "reusable system model", "reusable system models",
    "configurable model", "configurable models", "configurable system model",
    "configurable system models", "model template", "model templates",
)
GMISSION_TERMS = (
    "mission-agnostic", "mission agnostic", "mission-independent", "mission independent",
)
GMISSION_EXACT_TERMS = (
    "mission-agnostic model", "mission-agnostic models", "mission-agnostic architecture",
    "mission-agnostic architectures", "mission agnostic model", "mission agnostic models",
    "mission agnostic architecture", "mission agnostic architectures", "mission-independent model",
    "mission-independent models", "mission-independent architecture",
    "mission-independent architectures", "mission independent model", "mission independent models",
    "mission independent architecture", "mission independent architectures",
)

GSTRUCTURE_FIXED_TERMS = (
    "reference architecture", "reference architectures", "domain model", "domain models",
    "metamodel", "metamodels", "meta-model", "meta-models",
)
GPRODUCT_TERMS = ("product-line", "product line", "product-family", "product family")
GPRODUCT_EXACT_TERMS = (
    "product-line model", "product-line models", "product line model", "product line models",
    "product-family model", "product-family models", "product family model", "product family models",
)
GVARIATION_TERMS = ("variation point", "variation points")

C1_FIXED_TERMS = (
    "reference model", "reference models", "system reference model", "system reference models",
    "model library", "model libraries", "system model library", "system model libraries",
    "model pattern", "model patterns", "modeling pattern", "modeling patterns", "modelling pattern",
    "modelling patterns", "system model pattern", "system model patterns", "systems model pattern",
    "systems model patterns", "model profile", "model profiles", "system model profile",
    "system model profiles", "systems model profile", "systems model profiles", "SysML profile",
    "SysML profiles",
)
GDSL_TERMS = (
    "domain-specific modeling language", "domain specific modeling language",
    "domain-specific modelling language", "domain specific modelling language",
)

TPRECISE_TERMS = (
    "tailor", "tailors", "tailored", "tailoring", "customize", "customizes", "customized",
    "customizing", "customization", "customise", "customises", "customised", "customising",
    "customisation", "parameterize", "parameterizes", "parameterized", "parameterizing",
    "parameterization", "parameterise", "parameterises", "parameterised", "parameterising",
    "parameterisation", "instantiate", "instantiates", "instantiated", "instantiating",
    "instantiation", "variability", "variation point", "variation points",
)

ORDINARY_BLOCKS = {
    "P": ordinary_block(P_TERMS),
    "E_H": ordinary_block(EH_TERMS),
    "E_F": ordinary_block(EF_TERMS),
    "M_H": ordinary_block(MH_TERMS),
    "M_B": ordinary_block(MB_TERMS),
    "R": ordinary_block(R_TERMS),
    "G_model_fixed": ordinary_block(GMODEL_FIXED_TERMS),
    "G_mission": ordinary_block(GMISSION_TERMS),
    "G_mission_exact": ordinary_block(GMISSION_EXACT_TERMS),
    "G_structure_fixed": ordinary_block(GSTRUCTURE_FIXED_TERMS),
    "G_product": ordinary_block(GPRODUCT_TERMS),
    "G_product_exact": ordinary_block(GPRODUCT_EXACT_TERMS),
    "G_variation": ordinary_block(GVARIATION_TERMS),
    "C1_fixed": ordinary_block(C1_FIXED_TERMS),
    "G_DSL": ordinary_block(GDSL_TERMS),
    "T_precise": ordinary_block(TPRECISE_TERMS),
}

BLOCKS = {
    **ORDINARY_BLOCKS,
    "M": any_of(ORDINARY_BLOCKS["M_H"], ORDINARY_BLOCKS["M_B"]),
    "G_model": any_of(
        ORDINARY_BLOCKS["G_model_fixed"],
        ORDINARY_BLOCKS["G_mission_exact"],
        all_of(ORDINARY_BLOCKS["G_mission"], ORDINARY_BLOCKS["M_B"]),
    ),
    "G_structure": any_of(
        ORDINARY_BLOCKS["G_structure_fixed"],
        ORDINARY_BLOCKS["G_product_exact"],
        ORDINARY_BLOCKS["G_variation"],
        all_of(ORDINARY_BLOCKS["G_product"], ORDINARY_BLOCKS["M_B"]),
    ),
    "C1": any_of(ORDINARY_BLOCKS["C1_fixed"], ORDINARY_BLOCKS["G_DSL"]),
}

SCHEDULE = {
    "A1": all_of(BLOCKS["P"], BLOCKS["E_H"], BLOCKS["M_H"]),
    "A2": all_of(BLOCKS["P"], BLOCKS["E_F"], BLOCKS["M"]),
    "A3": all_of(BLOCKS["P"], BLOCKS["E_H"], BLOCKS["M_B"]),
    "B1": all_of(BLOCKS["P"], BLOCKS["M_H"]),
    "B2": all_of(BLOCKS["P"], BLOCKS["M_B"], BLOCKS["R"]),
    "BG1": all_of(BLOCKS["P"], BLOCKS["G_model"]),
    "BG2": all_of(BLOCKS["P"], BLOCKS["G_structure"]),
    "BC1": all_of(BLOCKS["P"], BLOCKS["C1"]),
    "BT2": all_of(BLOCKS["P"], BLOCKS["M_B"], BLOCKS["T_precise"]),
}

TERM_COUNTS = {
    "P": len(P_TERMS),
    "E_H": len(EH_TERMS),
    "E_F": len(EF_TERMS),
    "M_H": len(MH_TERMS),
    "M_B": len(MB_TERMS),
    "R": len(R_TERMS),
    "G_model_fixed": len(GMODEL_FIXED_TERMS),
    "G_mission": len(GMISSION_TERMS),
    "G_mission_exact": len(GMISSION_EXACT_TERMS),
    "G_structure_fixed": len(GSTRUCTURE_FIXED_TERMS),
    "G_product": len(GPRODUCT_TERMS),
    "G_product_exact": len(GPRODUCT_EXACT_TERMS),
    "G_variation": len(GVARIATION_TERMS),
    "C1_fixed": len(C1_FIXED_TERMS),
    "G_DSL": len(GDSL_TERMS),
    "T_precise": len(TPRECISE_TERMS),
}

EXPECTED_COUNTS = {
    "P": 26, "E_H": 38, "E_F": 37, "M_H": 54, "M_B": 31, "R": 55,
    "G_model_fixed": 14, "G_mission": 4, "G_mission_exact": 16,
    "G_structure_fixed": 8, "G_product": 4, "G_product_exact": 8,
    "G_variation": 2, "C1_fixed": 26, "G_DSL": 4, "T_precise": 32,
}

assert TERM_COUNTS == EXPECTED_COUNTS
assert tuple(SCHEDULE) == SCHEDULE_IDS
assert all("NEAR" not in query.upper() for query in SCHEDULE.values())
assert all("*" not in query and "?" not in query for query in SCHEDULE.values())
