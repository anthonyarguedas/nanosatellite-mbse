#!/usr/bin/env python3
"""Translate and attach the Space Segment composition predicate.

Usage: python3 convert_structure_rule.py DISTROTEMP [SYSML_PROFILE_MDZIP]

The chosen SysML v2 rule requires a direct composite spacecraft part. This
strengthens the Cameo expression, which only checks for any decomposition
result. The 2025 model has no explicit SpaceSegment stereotype applications. At the
user's direction, the generated assertion applies to the Space Segment class,
which has the broader Segment stereotype. The user chose all nine CubeSat
subsystem parts for the mass rollup, a set-level orbit binding in Space Segment,
and 30 compatible component contributors. Two shared processor parts stay
outside the rollup. Run convert_mass_rollup.py and
convert_remaining_architecture.py first, then convert_unit_imports.py.
"""

import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
SOURCE = "CSRM - 2025-11-18.mdzip"
PROFILE = "CSRM-Profile2.mdzip"
OPERATION_ID = "_19_0_2_8cb028a_1542813352853_268760_4957"
RULE_ID = "_2022x_2_2b0010b_1698606921881_949808_22493"
DEFAULT_SYSML_PROFILE = Path("/Applications/Magic Systems of Systems Architect/profiles/SysML Profile.mdzip")


def read_root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def unique(items, description):
    result = list(items)
    if len(result) != 1:
        raise ValueError(f"Expected one {description}, found {len(result)}")
    return result[0]


def named(parent, name):
    return unique((child for child in parent if child.get("name") == name), name)


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def quote(name):
    ensure("'" not in name and "\n" not in name and "\r" not in name,
           f"Source name needs SysML escaping: {name!r}")
    return "'" + name + "'"


def verify_expression(rule, installed_profile):
    specification = unique(rule.findall("specification"), "rule specification")
    ensure(specification.findtext("language") == "StructuredExpression", "Unexpected rule language")
    expr = ET.fromstring(specification.findtext("body"))
    ensure(local(expr) == "unionExpressionSpecification", "Unexpected rule root")
    outer = unique((child for child in expr if local(child) == "value"), "rule value")
    ensure(outer.get(XSI_TYPE) == "callExpressionSpecification", "Expected not call")
    empty = unique((child for child in outer if local(child) == "argument"), "not argument")
    ensure(empty.get(XSI_TYPE) == "callExpressionSpecification", "Expected IsEmpty call")
    decomposition = unique((child for child in empty if local(child) == "argument"), "IsEmpty argument")
    ensure(decomposition.get(XSI_TYPE) == "callExpressionSpecification", "Expected decomposition call")
    args = [child for child in decomposition if local(child) == "argument"]
    ensure(len(args) == 2 and args[0].get(XSI_TYPE) == "lookupExpressionSpecification" and
           args[0].get("symbol") == "THIS" and args[1].get(XSI_TYPE) == "booleanExpressionSpecification" and
           args[1].get("value") == "true", "Unexpected decomposition arguments")
    expected_calls = ((outer, "_19_0beta_8ca0285_1502101213659_906613_4522"),
                      (empty, "_19_0beta_8ca0285_1502101213659_300258_4511"),
                      (decomposition, OPERATION_ID))
    for call, ident in expected_calls:
        elements = call.findall("{*}expression/{*}element")
        ensure(len(elements) == 1 and elements[0].get("element") == ident,
               f"Unexpected behavior ID in call: {ident}")
    ensure(len([node for node in expr.iter() if node.get(XSI_TYPE) == "callExpressionSpecification"]) == 3,
           "Additional rule call needs translation")
    op = unique((e for e in installed_profile.iter() if e.get(XMI + "id") == OPERATION_ID), "installed behavior")
    ensure(op.get("name") == "StructureDecomposition" and op.findtext("language") == "Binary" and
           op.findtext("body") == "com.nomagic.magicdraw.sysml.expressions.StructureDecompositionExpression", "Unexpected installed operator")
    ensure([(p.get("name"), p.get("direction", "in")) for p in op.findall("ownedParameter")] ==
           [("element", "in"), ("includeInherited", "in"), ("result", "return")],
           "Unexpected decomposition signature")


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    source_dir = Path(sys.argv[1])
    installed = Path(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_SYSML_PROFILE
    root = read_root(source_dir / SOURCE, "com.nomagic.magicdraw.uml_model.model")
    profile = read_root(source_dir / PROFILE, "com.nomagic.magicdraw.uml_model.shared_model")
    installed_profile = read_root(installed, "com.nomagic.magicdraw.uml_model.shared_model")
    ids = {el.get(XMI + "id"): el for el in root.iter() if el.get(XMI + "id")}
    profile_ids = {el.get(XMI + "id"): el for el in profile.iter() if el.get(XMI + "id")}
    parents = {child: owner for owner in root.iter() for child in owner}

    def path(el):
        names = []
        while el is not None:
            if el.get("name"):
                names.insert(0, el.get("name"))
            el = parents.get(el)
        return "::".join(names)

    def stereotype(name):
        return unique((el for el in profile_ids.values()
                       if el.get(XMI + "type") == "uml:Stereotype" and el.get("name") == name), name)

    model = named(root, "Data")
    extensions = named(model, "CSRM Extentions")
    structure = named(named(extensions, "Model Constraints"), "Structure")
    rule = named(structure, "Space Segment Compostion")
    ensure(rule.get(XMI + "type") == "uml:Constraint" and rule.get(XMI + "id") == RULE_ID,
           "Unexpected source rule")
    scope = PROFILE + "#" + stereotype("SpaceSegment").get(XMI + "id")
    ensure([el.get("href") for el in rule.findall("constrainedElement")] == [scope],
           "Unexpected source rule scope")
    verify_expression(rule, installed_profile)
    comment = unique(rule.findall("ownedComment"), "rule comment").get("body")
    ensure(comment == "This is a completeness check to ensure the space segment has a spacecraft.",
           "Rule intent comment changed")
    validation = unique((app for app in root if app.get("base_Constraint") == RULE_ID), "rule settings")
    ensure(validation.get("severity") == "warning" and
           validation.get("errorMessage") == "Space Segment must be composed of one or more Spacecraft.",
           "Unexpected rule severity or message")

    chain = ("Spacecraft", "Satellite", "CubeSat")
    types = {name: stereotype(name) for name in chain}
    for child, parent in zip(chain[1:], chain[:-1]):
        gens = types[child].findall("generalization")
        ensure(len(gens) == 1 and gens[0].get("general") == types[parent].get(XMI + "id"),
               f"Unexpected {child} stereotype inheritance")
    scoped = [app.get("base_Class") for app in root
              if local(app) == "SpaceSegment" and app.get("base_Class")]
    ensure(not scoped, "Source SpaceSegment instances need asserted validation usages")
    segment = unique((el for el in root.iter() if el.get(XMI + "type") == "uml:Class" and
                      el.get("name") == "Space Segment"), "Space Segment class")
    segment_id = segment.get(XMI + "id")
    ensure(len([app for app in root if local(app) == "Segment" and app.get("base_Class") == segment_id]) == 1,
           "Source Space Segment stereotype changed")
    parts = segment.findall("ownedAttribute")
    ensure(len(parts) == 2 and {part.get("name") for part in parts} == {"cubeSat", "cubeSat Orbit"} and
           all(part.get("aggregation") == "composite" for part in parts), "Source structure changed")
    cube = unique((part for part in parts if part.get("name") == "cubeSat"), "cubeSat part")
    cube_type = ids[cube.get("type")]
    ensure(cube_type.get(XMI + "type") == "uml:Class" and cube_type.get("name") == "CubeSat" and
           len([app for app in root if local(app) == "CubeSat" and
                app.get("base_Class") == cube_type.get(XMI + "id")]) == 1,
           "cubeSat type or stereotype changed")
    orbit_part = unique((part for part in parts if part.get("name") == "cubeSat Orbit"), "orbit part")
    orbit_type = ids[orbit_part.get("type")]
    ensure(orbit_type.get(XMI + "type") == "uml:Class" and orbit_type.get("name") == "CubeSat Orbit" and
           len([app for app in root if local(app) == "Block" and
                app.get("base_Class") == orbit_type.get(XMI + "id")]) == 1,
           "Orbit source type or Block stereotype changed")
    ensure(parents[segment] is parents[cube_type] is parents[orbit_type] and
           path(parents[segment]) == "Data::5 - Architecture::L2_Segment::L2.1_Space Segment::L2.1.2_Structures",
           "Structure class namespace changed")
    ensure(len(cube_type.findall("ownedAttribute")) == 10 and
           len(orbit_type.findall("ownedAttribute")) == 7,
           "Partial class stubs need more content")
    orbit_reference = unique((part for part in cube_type.findall("ownedAttribute")
                              if part.get("name") == "Orbit"), "CubeSat Orbit reference")
    ensure(orbit_reference.get(XMI + "type") == "uml:Property" and
           orbit_reference.get("type") is None and orbit_reference.find("type") is None and
           orbit_reference.get("association") is None and orbit_reference.get("aggregation") is None and
           len(list(orbit_reference)) == 0 and
           len([app for app in root if local(app) == "ReferenceProperty" and
                app.get("base_Property") == orbit_reference.get(XMI + "id")]) == 1 and
           not segment.findall("ownedConnector") and not cube_type.findall("ownedConnector"),
           "Orbit reference or source binding changed")
    orbit_values = orbit_type.findall("ownedAttribute")
    ensure([p.get("name") for p in orbit_values] == [
        "eccentricity", "semi-major axis", "inclination", "longitude of ascending node",
        "argument of perigee", "true anomaly at epoch", "time of epoch",
    ], "Source orbit value properties changed")
    for prop in orbit_values:
        ensure(set(prop.attrib) == {XMI + "type", XMI + "id", "name", "aggregation"} and
               prop.get(XMI + "type") == "uml:Property" and
               prop.get("aggregation") == "composite" and len(prop) == 0 and
               len([app for app in root if local(app) == "ValueProperty" and
                    app.get("base_Property") == prop.get(XMI + "id")]) == 1,
               f"Orbit value property needs an explicit type decision: {prop.get('name')}")
    generalization = unique(cube_type.findall("generalization"), "CubeSat generalization")
    general_ref = unique(generalization.findall("general"), "CubeSat general target").get("href")
    ensure(general_ref == "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312269_537593_13833",
           "CubeSat external superclass changed")
    block = unique((el for el in installed_profile.iter() if el.get("name") == "Block" and
                    el.get(XMI + "type") == "uml:Stereotype"), "SysML Block stereotype")
    segment_app = stereotype("Segment")
    for part in parts:
        ensure(part.get(XMI + "type") == "uml:Property" and part.get("visibility") == "public" and
               len(part.findall("upperValue")) == 1 and part.find("upperValue").get("value") == "*" and
               not part.findall("lowerValue") and part.get("association") and
               len([app for app in root if local(app) == "PartProperty" and
                    app.get("base_Property") == part.get(XMI + "id")]) == 1,
               f"Unexpected source part property: {part.get('name')}")

    out = Path(__file__).resolve().parent
    remainder = json.loads((out / "architecture-remainder.fragment.json").read_text())
    ensure(remainder["sourceArchive"] == SOURCE and
           remainder["sourceArchiveSha256"] == hashlib.sha256((source_dir / SOURCE).read_bytes()).hexdigest(),
           "Regenerate the remaining architecture branches from this source archive")
    branches = remainder["branches"]
    ensure(set(branches) == {"L0_Domain", "L1_Mission", "L2_Segment", "L3_Subsystems",
                             "L4_Components", "Facilities"} and
           all(isinstance(lines, list) and all(isinstance(line, str) for line in lines)
               for lines in branches.values()), "Unexpected architecture branch fragments")
    rollup_file = out / "mass-rollup-source-audit.json"
    ensure(rollup_file.exists(), "Run convert_mass_rollup.py before converting the structure rule")
    rollup_audit = json.loads(rollup_file.read_text())
    ensure(rollup_audit["patternRef"] == general_ref and
           rollup_audit["sourceCubeSatClassRef"] == SOURCE + "#" + cube_type.get(XMI + "id") and
           rollup_audit["sourceGeneralizationRef"] == SOURCE + "#" + generalization.get(XMI + "id") and
           rollup_audit["sourceSubMassSubsettingCount"] == 0 and
           rollup_audit["convertedSubMassSubsettingCount"] == 9 and
           rollup_audit["subMassChoice"] == "user-authorized: all nine direct CubeSat subsystem parts",
           "Mass rollup evidence differs from the source structure")
    subsystem_entries = rollup_audit["cubeSatSubsystemParts"]
    subsystem_parts = [part for part in cube_type.findall("ownedAttribute")
                       if part.get("aggregation") == "composite"]
    ensure(len(subsystem_entries) == len(subsystem_parts) == 9 and all(
        entry["sourceRef"] == SOURCE + "#" + part.get(XMI + "id") and
        entry["name"] == part.get("name") and
        entry["typeRef"] == SOURCE + "#" + part.get("type") and
        entry["associationRef"] == SOURCE + "#" + part.get("association") and
        entry["sourceMultiplicity"] == "1..1" and
        entry["convertedSubsets"] == rollup_audit["sourcePropertyRefs"]["subMass"]
        for entry, part in zip(subsystem_entries, subsystem_parts)),
        "Mass rollup contributor audit no longer matches the source class")
    subsystems = [ids[part.get("type")] for part in subsystem_parts]
    subsystem_stereo = stereotype("Subsystem")
    for cls in subsystems:
        ensure(path(parents[cls]) ==
               "Data::5 - Architecture::L3_Subsystems::L3.1_CubeSat Subsystems::L3.1.2_Structures" and
               cls.get(XMI + "type") == "uml:Class" and
               len([app for app in root if local(app) == "Subsystem" and
                    app.get("base_Class") == cls.get(XMI + "id")]) == 1,
               f"Unexpected subsystem class or stereotype: {cls.get('name')}")
    component_records = []
    for cls in subsystems:
        for part in cls.findall("ownedAttribute"):
            typ = ids[part.get("type")]
            compatible = any(g.get("href") == general_ref
                             for gen in typ.findall("generalization") for g in gen.findall("general"))
            component_records.append((cls, part, typ, compatible))
    component_entries = rollup_audit["subsystemComponentParts"]
    ensure(len(component_records) == len(component_entries) == 32 and
           rollup_audit["convertedComponentSubMassSubsettingCount"] == 30 and
           rollup_audit["excludedSharedProcessorPartCount"] == 2 and
           rollup_audit["componentChoice"] ==
           "user-authorized: 30 compatible components subset subMass; two shared processors stay out" and
           rollup_audit["sharedProcessorCompositionChoice"] ==
           "user-authorized: retain two separate composite parts, no shared instance" and all(
               entry["ownerRef"] == SOURCE + "#" + cls.get(XMI + "id") and
               entry["name"] == part.get("name") and
               entry["sourceRef"] == SOURCE + "#" + part.get(XMI + "id") and
               entry["typeRef"] == SOURCE + "#" + typ.get(XMI + "id") and
               entry["associationRef"] == SOURCE + "#" + part.get("association") and
               entry["sourceMultiplicity"] == "1..1" and not entry["sourceHadSubsetting"] and
               entry["convertedSubsets"] ==
               (rollup_audit["sourcePropertyRefs"]["subMass"] if compatible else "")
               for entry, (cls, part, typ, compatible) in zip(component_entries, component_records)),
           "Component rollup audit does not match the source model")
    component_stereo = stereotype("Component")
    component_types = list(dict.fromkeys(typ for _, _, typ, _ in component_records))
    ensure(len(component_types) == 31 and
           sum(compatible for _, _, _, compatible in component_records) == 30,
           "Unexpected component classifiers or rollup contributors")
    for typ in component_types:
        ensure(path(parents[typ]).startswith("Data::5 - Architecture::L4_Components::") and
               typ.get(XMI + "type") == "uml:Class" and
               len([app for app in root if local(app) == "Component" and
                    app.get("base_Class") == typ.get(XMI + "id")]) == 1 and
               not typ.findall("ownedAttribute"),
               f"Component class needs additional conversion: {typ.get('name')}")
    report = {
        "rule": rule.get("name"),
        "ruleId": RULE_ID,
        "ruleComment": comment,
        "sourceExpression": "not(IsEmpty(StructureDecomposition1(THIS, true)))",
        "behaviorRef": "SysML Profile.mdzip#" + OPERATION_ID,
        "installedBehaviorSecondParameter": "includeInherited",
        "scopeRef": scope,
        "sourceExplicitSpaceSegmentApplications": scoped,
        "cameoSeverity": validation.get("severity"),
        "cameoRuleExecution": "not run",
        "chosenPredicate": "at least one direct composite part typed by Spacecraft or a subtype",
        "sourcePredicateDifference": "StructureDecomposition also counts non-composite properties, ports, and other owned elements",
        "candidate": {
            "class": path(segment),
            "classId": segment_id,
            "appliedStereotype": "Segment",
            "directCompositeParts": [{"name": part.get("name"), "propertyId": part.get(XMI + "id"),
                                      "type": path(ids[part.get("type")]), "typeId": part.get("type")}
                                     for part in parts],
            "cubeSatStereotypeHierarchy": list(reversed(chain)),
            "scopeDecision": "user-authorized: attach to Segment class despite missing SpaceSegment application",
            "assertedRuleOnClass": "Space Segment",
            "convertedCubeSatGeneralizationRef": general_ref,
            "subMassChildDecision": "user-authorized: all nine subsystem parts subset subMass",
            "convertedCubeSatSubsystemParts": 9,
            "convertedSubsystemComponentParts": 32,
            "convertedComponentRollUpContributors": 30,
            "excludedSharedProcessorParts": [SOURCE + "#" + part.get(XMI + "id")
                                             for _, part, _, compatible in component_records if not compatible],
            "sharedProcessorCompositionChoice": rollup_audit["sharedProcessorCompositionChoice"],
            "deferredCubeSatOwnedProperties": 0,
            "deferredOrbitOwnedProperties": 0,
            "untypedOrbitValueProperties": [
                {"name": prop.get("name"), "sourceRef": SOURCE + "#" + prop.get(XMI + "id"),
                 "sourceHadType": False, "sourceQuantityKindRef": "", "sourceUnitRef": "",
                 "sourceMultiplicity": "1..1"} for prop in orbit_values
            ],
            "chosenOrbitReference": {
                "sourceRef": SOURCE + "#" + orbit_reference.get(XMI + "id"),
                "sourceHadType": False,
                "sourceHadBinding": False,
                "chosenTypeRef": SOURCE + "#" + orbit_type.get(XMI + "id"),
                "chosenTargetPartRef": SOURCE + "#" + orbit_part.get(XMI + "id"),
                "sourceMultiplicity": "1..1",
                "bindingContext": path(segment),
                "interpretation": "user-authorized collection-level binding, no pairing of individual CubeSats and orbits",
            },
        },
    }
    (out / "structure-source-audit.json").write_text(json.dumps(report, indent=2) + "\n")

    # These are source class shells, separate from the native stereotype types.
    # Preserve the source properties needed to bind the direct composition rule.
    lines = ["    // Converted 2025 architecture classes and their direct structure."]
    package_names = ("5 - Architecture", "L2_Segment", "L2.1_Space Segment", "L2.1.2_Structures")
    for level, name in enumerate(package_names, start=1):
        lines.append("    " * level + f"package {quote(name)} {{")
    indent = "    " * (len(package_names) + 1)

    def class_source(element, ref, prefix=indent):
        return [prefix + "    @CSRMv1Metadata::ConvertedClassSource {",
                prefix + f"        sourceRef = {json.dumps(SOURCE + '#' + element.get(XMI + 'id'))};",
                prefix + f"        stereotypeRef = {json.dumps(ref)};",
                prefix + '        sourceSummary = "";',
                prefix + '        sourceId = "";',
                prefix + "    }"]

    lines.append(indent + "part def CubeSat :> CSRMNativeStructures::CubeSat, CSRMMassRollUp::MassRollUpPattern {")
    lines.extend(class_source(cube_type, PROFILE + "#" + types["CubeSat"].get(XMI + "id")))
    for part, cls in zip(subsystem_parts, subsystems):
        type_name = "Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::" + quote(cls.get("name"))
        lines.extend([
            indent + f"    part {quote(part.get('name'))} : {type_name} [1..1] :> subMass {{",
            indent + "        @CSRMv1Metadata::ConvertedPartSource {",
            indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
            indent + f"            associationRef = {json.dumps(SOURCE + '#' + part.get('association'))};",
            indent + f"            sourceTypeRef = {json.dumps(SOURCE + '#' + cls.get(XMI + 'id'))};",
            indent + '            sourceMultiplicity = "1..1";',
            indent + "        }",
            indent + "        @CSRMv1Metadata::ChosenRollUpSubsetting {",
            indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
            indent + f"            chosenTargetRef = {json.dumps(rollup_audit['sourcePropertyRefs']['subMass'])};",
            indent + "            isSourceSubsetting = false;",
            indent + "        }",
            indent + "    }",
        ])
    orbit_type_path = "Data::'5 - Architecture'::L2_Segment::'L2.1_Space Segment'::'L2.1.2_Structures'::" + quote(orbit_type.get("name"))
    lines.extend([
        indent + f"    ref part {quote(orbit_reference.get('name'))} : {orbit_type_path} [1..1] {{",
        indent + "        @CSRMv1Metadata::ChosenOrbitReference {",
        indent + f"            sourceRef = {json.dumps(SOURCE + '#' + orbit_reference.get(XMI + 'id'))};",
        indent + f"            chosenTypeRef = {json.dumps(SOURCE + '#' + orbit_type.get(XMI + 'id'))};",
        indent + "            sourceHadType = false;",
        indent + '            sourceMultiplicity = "1..1";',
        indent + "        }",
        indent + "    }",
        indent + "}",
        indent + f"part def {quote(orbit_type.get('name'))} {{",
    ])
    lines.extend(class_source(orbit_type, "SysML Profile.mdzip#" + block.get(XMI + "id")))
    for prop in orbit_values:
        lines.extend([
            indent + f"    attribute {quote(prop.get('name'))} [1..1] {{",
            indent + "        @CSRMv1Metadata::UntypedValuePropertySource {",
            indent + f"            sourceRef = {json.dumps(SOURCE + '#' + prop.get(XMI + 'id'))};",
            indent + '            sourceKind = "SysML v1 ValueProperty";',
            indent + "            sourceHadType = false;",
            indent + '            sourceMultiplicity = "1..1";',
            indent + '            sourceAggregation = "composite";',
            indent + '            quantityKindRef = "";',
            indent + '            unitRef = "";',
            indent + "        }",
            indent + "    }",
        ])
    lines.extend([indent + "}",
                  indent + f"part def {quote(segment.get('name'))} {{"])
    lines.extend(class_source(segment, PROFILE + "#" + segment_app.get(XMI + "id")))
    for part in parts:
        declared_type = cube_type if part is cube else orbit_type
        lines.extend([
            indent + f"    part {quote(part.get('name'))} : {quote(declared_type.get('name'))} [1..*] {{",
            indent + "        @CSRMv1Metadata::ConvertedPartSource {",
            indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
            indent + f"            associationRef = {json.dumps(SOURCE + '#' + part.get('association'))};",
            indent + f"            sourceTypeRef = {json.dumps(SOURCE + '#' + declared_type.get(XMI + 'id'))};",
            indent + '            sourceMultiplicity = "1..*";',
            indent + "        }",
            indent + "    }",
        ])
    lines.extend([
        indent + f"    binding orbitBinding bind cubeSat.{quote(orbit_reference.get('name'))} = {quote(orbit_part.get('name'))} {{",
        indent + "        @CSRMv1Metadata::ChosenOrbitBinding {",
        indent + f"            sourceRef = {json.dumps(SOURCE + '#' + orbit_reference.get(XMI + 'id'))};",
        indent + f"            chosenTargetRef = {json.dumps(SOURCE + '#' + orbit_part.get(XMI + 'id'))};",
        indent + "            sourceHadBinding = false;",
        indent + '            interpretation = "User chose collection-level binding without per-CubeSat pairing";',
        indent + "        }",
        indent + "    }",
        indent + "    assert constraint spacecraftCompositionValidation : CSRMStructureValidation::'Space Segment Compostion' {",
        indent + "        @CSRMv1Metadata::ExpandedValidationScope {",
        indent + f"            sourceRef = {json.dumps(SOURCE + '#' + RULE_ID)};",
        indent + f"            originalScopeRef = {json.dumps(scope)};",
        indent + f"            appliedClassRef = {json.dumps(SOURCE + '#' + segment_id)};",
        indent + '            decision = "User authorized applying the SpaceSegment rule to a Segment class";',
        indent + "        }",
        indent + "        in ref part directSpacecraftParts = cubeSat;",
        indent + "    }",
        indent + "}",
    ])
    for level in range(len(package_names), 1, -1):
        if level == 2:
            lines.extend(branches["L2_Segment"])
        lines.append("    " * level + "}")
    for level, name in enumerate(("L3_Subsystems", "L3.1_CubeSat Subsystems", "L3.1.2_Structures"), start=2):
        lines.append("    " * level + f"package {quote(name)} {{")
    for cls in subsystems:
        lines.append(indent + f"part def {quote(cls.get('name'))} :> CSRMMassRollUp::MassRollUpPattern {{")
        lines.extend(class_source(cls, PROFILE + "#" + subsystem_stereo.get(XMI + "id")))
        for _, part, typ, compatible in (row for row in component_records if row[0] is cls):
            type_path = "::".join(quote(name) for name in path(typ).split("::"))
            part_name = " " + quote(part.get("name")) if part.get("name") else ""
            subset = " :> subMass" if compatible else ""
            lines.extend([
                indent + f"    part{part_name} : {type_path} [1..1]{subset} {{",
                indent + "        @CSRMv1Metadata::ConvertedPartSource {",
                indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
                indent + f"            associationRef = {json.dumps(SOURCE + '#' + part.get('association'))};",
                indent + f"            sourceTypeRef = {json.dumps(SOURCE + '#' + typ.get(XMI + 'id'))};",
                indent + '            sourceMultiplicity = "1..1";',
                indent + "        }",
            ])
            if compatible:
                lines.extend([
                    indent + "        @CSRMv1Metadata::ChosenRollUpSubsetting {",
                    indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
                    indent + f"            chosenTargetRef = {json.dumps(rollup_audit['sourcePropertyRefs']['subMass'])};",
                    indent + "            isSourceSubsetting = false;",
                    indent + "        }",
                ])
            else:
                lines.extend([
                    indent + "        @CSRMv1Metadata::ExcludedRollUpContributor {",
                    indent + f"            sourceRef = {json.dumps(SOURCE + '#' + part.get(XMI + 'id'))};",
                    indent + f"            sourceTypeRef = {json.dumps(SOURCE + '#' + typ.get(XMI + 'id'))};",
                    indent + '            reason = "Separate composite part; user kept shared processor outside mass rollup";',
                    indent + "        }",
                ])
            lines.append(indent + "    }")
        lines.append(indent + "}")
    for level in range(len(package_names), 1, -1):
        if level == 2:
            lines.extend(branches["L3_Subsystems"])
        lines.append("    " * level + "}")

    def branch():
        return {"packages": OrderedDict(), "classes": []}

    component_tree = branch()
    for typ in component_types:
        parents_path = path(parents[typ]).split("::")
        ensure(parents_path[:3] == ["Data", "5 - Architecture", "L4_Components"],
               f"Unexpected component owner: {parents_path}")
        node = component_tree
        for name in parents_path[2:]:
            node = node["packages"].setdefault(name, branch())
        node["classes"].append(typ)

    def emit_components(node, level):
        prefix = "    " * level
        for name, child in node["packages"].items():
            lines.append(prefix + f"package {quote(name)} {{")
            emit_components(child, level + 1)
            if name == "L4_Components" and level == 2:
                lines.extend(branches["L4_Components"])
            lines.append(prefix + "}")
        for typ in node["classes"]:
            compatible = any(gen.get("href") == general_ref for g in typ.findall("generalization")
                             for gen in g.findall("general"))
            supertype = " :> CSRMMassRollUp::MassRollUpPattern" if compatible else ""
            lines.append(prefix + f"part def {quote(typ.get('name'))}{supertype} {{")
            lines.extend(class_source(typ, PROFILE + "#" + component_stereo.get(XMI + "id"), prefix))
            lines.append(prefix + "}")

    emit_components(component_tree, 2)
    for name in ("L0_Domain", "L1_Mission", "Facilities"):
        lines.extend(branches[name])
    lines.append("    }")
    (out / "architecture-structures.fragment").write_text("\n".join(lines) + "\n")

    lines = ["// CSRM architecture stereotypes as native part types, not source UML classes.",
             "package CSRMNativeStructures {"]
    for name in chain:
        parent = " :> " + chain[chain.index(name) - 1] if name != chain[0] else ""
        ref = PROFILE + "#" + types[name].get(XMI + "id")
        lines.extend([f"    part def {name}{parent} {{",
                      "        @CSRMv1Metadata::NativeStructureTypeSource {",
                      f"            sourceRef = {json.dumps(ref)};",
                      '            sourceKind = "CSRM UML Class stereotype";',
                      "        }", "    }"])
    lines.append("}")
    (out / "native-structures.sysml").write_text("\n".join(lines) + "\n")
    lines = ["// The 2025 source has no SpaceSegment applications. The user authorized a scope expansion.",
             "package CSRMStructureValidation {",
             "    constraint def 'Space Segment Compostion' {",
             "        @CSRMv1Metadata::ValidationRuleSource {",
             f"            sourceRef = {json.dumps(SOURCE + '#' + RULE_ID)};",
             f"            scopeRef = {json.dumps(scope)};",
             f"            targetRef = {json.dumps(PROFILE + '#' + types['Spacecraft'].get(XMI + 'id'))};",
             '            relation = "Chosen: at least one direct composite spacecraft part, not the original decomposition predicate";',
             "        }",
             "        in ref part directSpacecraftParts : CSRMNativeStructures::Spacecraft [0..*];",
             "        SequenceFunctions::size(directSpacecraftParts) > 0",
             "    }", "}"]
    (out / "structure-validation.sysml").write_text("\n".join(lines) + "\n")
    print("Wrote structure rule and all 2025 architecture classes and composite properties")


if __name__ == "__main__":
    main()
