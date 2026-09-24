#!/usr/bin/env python3
"""Reimplement MassRollUpPattern and audit its subsystem and component contributors.

Usage: python3 convert_mass_rollup.py DISTROTEMP [MD_CUSTOMIZATION_MDZIP]

Run before convert_structure_rule.py, which gives CubeSat this part definition
as an additional superclass. The source CubeSat has no property subsetting the
pattern's derived union subMass. The user chose all nine direct subsystem parts,
then 30 compatible component parts. Two shared processor parts stay outside it.
"""

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
SOURCE = "CSRM - 2025-11-18.mdzip"
LIBRARY = "MD_customization_for_SysML.mdzip"
PATTERN_ID = "_18_3_903028d_1448291312269_537593_13833"
CUBE_ID = "_18_0_6_3e4019a_1472151573832_997891_14609"
DEFAULT_LIBRARY = Path("/Applications/Magic Systems of Systems Architect/profiles") / LIBRARY


def root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def only(items, description):
    items = list(items)
    if len(items) != 1:
        raise ValueError(f"Expected one {description}, found {len(items)}")
    return items[0]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    source = root(Path(sys.argv[1]) / SOURCE, "com.nomagic.magicdraw.uml_model.model")
    lib_path = Path(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_LIBRARY
    library = root(lib_path, "com.nomagic.magicdraw.uml_model.shared_model")
    ids = {e.get(XMI + "id"): e for e in library.iter() if e.get(XMI + "id")}
    src_ids = {e.get(XMI + "id"): e for e in source.iter() if e.get(XMI + "id")}
    pattern = ids[PATTERN_ID]
    check(pattern.get(XMI + "type") == "uml:Class" and pattern.get("name") == "MassRollUpPattern",
          "Unexpected mass rollup pattern")
    check(len([app for app in library if local(app) == "Block" and
               app.get("base_Class") == PATTERN_ID]) == 1, "Expected a SysML v1 Block")
    attrs = {e.get("name"): e for e in pattern.findall("ownedAttribute")}
    check(set(attrs) == {"subMass", "mass", "totalMass", "sum"}, "Unexpected mass rollup attributes")
    sub_mass, mass, total_mass, sum_prop = (attrs[n] for n in ("subMass", "mass", "totalMass", "sum"))
    check(sub_mass.get("type") == PATTERN_ID and sub_mass.get("isDerivedUnion") == "true" and
          sub_mass.get("aggregation") == "composite" and
          only(sub_mass.findall("lowerValue"), "subMass lower").get("value") is None and
          only(sub_mass.findall("upperValue"), "subMass upper").get("value") == "*",
          "Unexpected derived union subMass")
    real = "http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML_dataType.Real"
    check(only(mass.findall("type"), "mass type").get("href") == real and
          only(total_mass.findall("type"), "totalMass type").get("href") == real and
          total_mass.get("isDerived") == "true", "Unexpected mass value types")
    default = only(mass.findall("defaultValue"), "mass default")
    check(default.get(XMI + "type") == "uml:LiteralReal" and default.get("value") is None,
          "Mass default is no longer the UML LiteralReal default 0.0")
    block = ids[sum_prop.get("type")]
    check(block.get(XMI + "type") == "uml:Class" and block.get("name") == "total" and
          len([app for app in library if local(app) == "ConstraintBlock" and
               app.get("base_Class") == block.get(XMI + "id")]) == 1,
          "Unexpected constraint block")
    rule = only(block.findall("ownedRule"), "rollup equation")
    spec = only(rule.findall("specification"), "rollup specification")
    check(rule.get("name") == "total" and spec.findtext("body") == "total = parent + sum(child)" and
          not spec.findtext("language"), "Unexpected mass equation")
    ports = {p.get("name"): p for p in block.findall("ownedAttribute")}
    check(set(ports) == {"parent", "child", "total"} and
          all(p.get(XMI + "type") == "uml:Port" and
              only(p.findall("type"), "constraint port type").get("href") == real
              for p in ports.values()), "Unexpected constraint ports")
    check(only(ports["child"].findall("lowerValue"), "child lower").get("value") is None and
          only(ports["child"].findall("upperValue"), "child upper").get("value") == "*",
          "Unexpected child multiplicity")

    # The nested connector end on totalMass identifies subMass.totalMass.
    nested = {app.get("base_ConnectorEnd"): app.get("propertyPath") for app in library
              if local(app) == "NestedConnectorEnd" and app.get("base_ConnectorEnd")}
    role = {p.get(XMI + "id"): p.get("name") for p in list(attrs.values()) + list(ports.values())}
    bindings = {}
    connectors = pattern.findall("ownedConnector")
    check(len(connectors) == 3, "Unexpected number of pattern connectors")
    for connector in connectors:
        check(len([app for app in library if local(app) == "BindingConnector" and
                   app.get("base_Connector") == connector.get(XMI + "id")]) == 1,
              "Expected binding connector")
        ends = connector.findall("end")
        check(len(ends) == 2, "Expected a binary binding")
        labels = []
        for end in ends:
            check(end.get("role") in role, "Unexpected connector role")
            label = role[end.get("role")]
            if end.get("partWithPort"):
                check(end.get("partWithPort") == sum_prop.get(XMI + "id"), "Unexpected constraint property")
                label = "sum." + label
            if end.get(XMI + "id") in nested:
                owner_id = nested[end.get(XMI + "id")]
                if owner_id == sub_mass.get(XMI + "id"):
                    label = "subMass." + label
                else:
                    check(owner_id == sum_prop.get(XMI + "id") and
                          end.get("partWithPort") == owner_id,
                          "Unexpected nested property path")
            labels.append(label)
        bindings[connector.get(XMI + "id")] = labels
    expected = {frozenset(pair) for pair in (("sum.parent", "mass"),
                                             ("sum.child", "subMass.totalMass"),
                                             ("sum.total", "totalMass"))}
    check({frozenset(pair) for pair in bindings.values()} == expected,
          "Pattern bindings do not implement totalMass = mass + sum(subMass.totalMass)")

    cube = src_ids[CUBE_ID]
    check(cube.get("name") == "CubeSat" and cube.get(XMI + "type") == "uml:Class", "Unexpected CubeSat class")
    generalization = only(cube.findall("generalization"), "CubeSat superclass")
    href = only(generalization.findall("general"), "CubeSat general target").get("href")
    check(href == LIBRARY + "#" + PATTERN_ID, "CubeSat mass rollup superclass changed")
    # Each direct subsystem class inherits the pattern, but its source part
    # property has no subsetting. The nine new subsettings are user-authorized.
    parts = [p for p in cube.findall("ownedAttribute") if p.get("aggregation") == "composite"]
    check(len(parts) == 9 and len({p.get("name") for p in parts}) == 9 and
          len({p.get("type") for p in parts}) == 9, "CubeSat subsystem set changed")
    for p in parts:
        part_type = src_ids[p.get("type")]
        check(p.get(XMI + "type") == "uml:Property" and p.get("association") and
              not p.findall("lowerValue") and not p.findall("upperValue") and
              not p.findall("subsettedProperty") and
              len([app for app in source if local(app) == "PartProperty" and
                   app.get("base_Property") == p.get(XMI + "id")]) == 1,
              f"Unexpected composite part property: {p.get('name')}")
        check(part_type.get(XMI + "type") == "uml:Class" and
              len([app for app in source if local(app) == "Subsystem" and
                   app.get("base_Class") == p.get("type")]) == 1 and
              len(part_type.findall("generalization")) == 1 and
              any(e.get("href") == href for gen in part_type.findall("generalization")
                  for e in gen.findall("general")),
              f"Subsystem {p.get('name')} no longer inherits the pattern")
    subset_refs = [e.get("href") or e.get(XMI + "idref") for e in source.iter()
                   if local(e) == "subsettedProperty"]
    check(PATTERN_ID not in subset_refs and sub_mass.get(XMI + "id") not in subset_refs and
          href not in subset_refs and LIBRARY + "#" + sub_mass.get(XMI + "id") not in subset_refs,
          "Source has new rollup child subsettings to translate")

    # Two uses of one shared component have no rollup superclass. Keep their
    # source composition, but do not add incompatible subMass subsettings.
    components = []
    for parent_part in parts:
        subsystem = src_ids[parent_part.get("type")]
        for prop in subsystem.findall("ownedAttribute"):
            part_type = src_ids[prop.get("type")]
            check(prop.get(XMI + "type") == "uml:Property" and
                  prop.get("visibility") == "public" and prop.get("aggregation") == "composite" and
                  prop.get("association") and len(prop) == 0 and
                  len([app for app in source if local(app) == "PartProperty" and
                       app.get("base_Property") == prop.get(XMI + "id")]) == 1 and
                  part_type.get(XMI + "type") == "uml:Class" and
                  len([app for app in source if local(app) == "Component" and
                       app.get("base_Class") == part_type.get(XMI + "id")]) == 1,
                  f"Unexpected subsystem component: {subsystem.get('name')}::{prop.get('name')}")
            compatible = any(e.get("href") == href for gen in part_type.findall("generalization")
                             for e in gen.findall("general"))
            check((compatible and len(part_type.findall("generalization")) == 1 or
                   not compatible and not part_type.findall("generalization")) and
                  not part_type.findall("ownedAttribute"),
                  f"Component type needs separate conversion: {part_type.get('name')}")
            components.append((subsystem, prop, part_type, compatible))
    excluded = [(owner.get("name"), prop.get("name"), typ.get(XMI + "id"))
                for owner, prop, typ, compatible in components if not compatible]
    check(len(components) == 32 and sum(c[3] for c in components) == 30 and
          len({c[2].get(XMI + "id") for c in components}) == 31 and
          excluded == [
              ("Attitude Determination and Control Subsystem", "shared Processor and Memory",
               "_18_4_1_3880181_1494340978082_527489_51171"),
              ("Guidance Navigation and Control Subsystem", "shared Processor and Memory",
               "_18_4_1_3880181_1494340978082_527489_51171"),
          ], "Expected 30 compatible components and two excluded shared processors")

    prefix = LIBRARY + "#"
    audit = {
        "sourceArchive": SOURCE,
        "patternRef": prefix + PATTERN_ID,
        "patternLibrary": str(lib_path),
        "equationRef": prefix + rule.get(XMI + "id"),
        "constraintBlockRef": prefix + block.get(XMI + "id"),
        "equation": spec.findtext("body"),
        "bindingConnectorIds": {prefix + key: value for key, value in bindings.items()},
        "sourcePropertyRefs": {name: prefix + el.get(XMI + "id") for name, el in attrs.items()},
        "sourceMassDefault": "UML LiteralReal with omitted value attribute (default 0.0)",
        "sourceQuantityKindOrUnit": "none: the pattern properties use SysML v1 primitive Real",
        "sourceCubeSatClassRef": SOURCE + "#" + CUBE_ID,
        "sourceGeneralizationRef": SOURCE + "#" + generalization.get(XMI + "id"),
        "subMassSourceMeaning": "composite derived union, 0..*, typed by MassRollUpPattern",
        "cubeSatSubsystemParts": [{"name": p.get("name"), "sourceRef": SOURCE + "#" + p.get(XMI + "id"),
                                   "typeRef": SOURCE + "#" + p.get("type"),
                                   "associationRef": SOURCE + "#" + p.get("association"),
                                   "sourceMultiplicity": "1..1",
                                   "convertedSubsets": prefix + sub_mass.get(XMI + "id")}
                                  for p in parts],
        "sourceSubMassSubsettingCount": 0,
        "convertedSubMassSubsettingCount": len(parts),
        "subMassChoice": "user-authorized: all nine direct CubeSat subsystem parts",
        "subsystemComponentParts": [
            {"ownerRef": SOURCE + "#" + owner.get(XMI + "id"),
             "name": prop.get("name"), "sourceRef": SOURCE + "#" + prop.get(XMI + "id"),
             "typeRef": SOURCE + "#" + typ.get(XMI + "id"),
             "associationRef": SOURCE + "#" + prop.get("association"),
             "sourceMultiplicity": "1..1", "sourceHadSubsetting": False,
             "convertedSubsets": prefix + sub_mass.get(XMI + "id") if compatible else ""}
            for owner, prop, typ, compatible in components
        ],
        "convertedComponentSubMassSubsettingCount": 30,
        "excludedSharedProcessorPartCount": 2,
        "componentChoice": "user-authorized: 30 compatible components subset subMass; two shared processors stay out",
        "sharedProcessorCompositionChoice": "user-authorized: retain two separate composite parts, no shared instance",
        "cameoSimulation": "not run",
    }
    lines = [
        "// Reimplemented SysML v1 mass rollup. No source unit or quantity kind is declared.",
        "// subMass is abstract. Nine CubeSat subsystem and 30 eligible component parts subset it.",
        "package CSRMMassRollUp {",
        "    calc def MassTotal {",
        "        @CSRMv1Metadata::MassRollUpSource {",
        f"            sourceRef = {json.dumps(prefix + block.get(XMI + 'id'))};",
        '            sourceKind = "SysML v1 ConstraintBlock total: total = parent + sum(child)";',
        "        }",
        "        in attribute parent : ScalarValues::Real;",
        "        in attribute child : ScalarValues::Real [0..*];",
        "        return attribute total : ScalarValues::Real;",
        "        parent + RealFunctions::sum(child)",
        "    }",
        "    part def MassRollUpPattern {",
        "        @CSRMv1Metadata::MassRollUpSource {",
        f"            sourceRef = {json.dumps(prefix + PATTERN_ID)};",
        '            sourceKind = "SysML v1 Block and rollup pattern";',
        "        }",
        "        abstract part subMass : MassRollUpPattern [0..*] {",
        "            @CSRMv1Metadata::MassRollUpSource {",
        f"                sourceRef = {json.dumps(prefix + sub_mass.get(XMI + 'id'))};",
        '                sourceKind = "composite derived union";',
        "            }",
        "        }",
        "        attribute mass : ScalarValues::Real default = 0.0 {",
        "            @CSRMv1Metadata::MassRollUpSource {",
        f"                sourceRef = {json.dumps(prefix + mass.get(XMI + 'id'))};",
        '                sourceKind = "SysML v1 Real ValueProperty with default 0.0";',
        "            }",
        "        }",
        "        derived attribute totalMass : ScalarValues::Real = MassTotal(mass, subMass.totalMass) {",
        "            @CSRMv1Metadata::MassRollUpSource {",
        f"                sourceRef = {json.dumps(prefix + total_mass.get(XMI + 'id'))};",
        '                sourceKind = "SysML v1 derived Real ValueProperty";',
        "            }",
        "        }",
        "    }",
        "}",
    ]
    out = Path(__file__).resolve().parent
    (out / "mass-rollup-source-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    (out / "mass-rollup.sysml").write_text("\n".join(lines) + "\n")
    print("Reimplemented mass rollup and audited nine subsystem plus 30 component contributors")


if __name__ == "__main__":
    main()
