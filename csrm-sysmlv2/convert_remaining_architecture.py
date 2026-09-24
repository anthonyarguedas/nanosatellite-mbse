#!/usr/bin/env python3
"""Convert the remaining 2025 architecture classes and composite properties.

Usage: python3 convert_remaining_architecture.py DISTROTEMP [SYSML_PROFILE_MDZIP]

Run before convert_structure_rule.py. Emit branch snippets for insertion into its
existing package declarations, so no duplicate package identities are created.
The source has no ground or facility mass rollup generalizations or subsettings.
"""

import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
SOURCE = "CSRM - 2025-11-18.mdzip"
PROFILE = "CSRM-Profile2.mdzip"
SYSML_PROFILE = "SysML Profile.mdzip"
DEFAULT_SYSML_PROFILE = Path("/Applications/Magic Systems of Systems Architect/profiles") / SYSML_PROFILE
EXPECTED = {"domain": (3, 3), "mission": (4, 5), "groundSegment": (1, 9),
            "groundSubsystems": (9, 26), "groundComponents": (26, 0),
            "facilities": (10, 8)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def archive_root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def quote(name):
    require(name is not None and "'" not in name and "\n" not in name and "\r" not in name,
            f"Identifier needs an explicit escaping decision: {name!r}")
    return "'" + name + "'"


def ref(element):
    return SOURCE + "#" + element.get(XMI + "id")


def package_tree():
    return {"packages": OrderedDict(), "classes": []}


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    source_dir = Path(sys.argv[1])
    sysml_profile = Path(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_SYSML_PROFILE
    source_file = source_dir / SOURCE
    profile_file = source_dir / PROFILE
    root = archive_root(source_file, "com.nomagic.magicdraw.uml_model.model")
    profile = archive_root(profile_file, "com.nomagic.magicdraw.uml_model.shared_model")
    installed = archive_root(sysml_profile, "com.nomagic.magicdraw.uml_model.shared_model")
    ids = {e.get(XMI + "id"): e for e in root.iter() if e.get(XMI + "id")}
    parents = {child: parent for parent in root.iter() for child in parent}

    def path(element):
        names = []
        while element is not None:
            if element.get("name"):
                names.insert(0, element.get("name"))
            element = parents.get(element)
        return names

    def one(items, description):
        items = list(items)
        require(len(items) == 1, f"Expected one {description}, found {len(items)}")
        return items[0]

    model = one((e for e in root if e.get("name") == "Data"), "Data model")
    arch = one((e for e in model if e.get("name") == "5 - Architecture"), "architecture package")
    require(arch.get(XMI + "type") == "uml:Package", "Unexpected architecture type")
    profile_types = {name: one((e for e in profile.iter() if e.get(XMI + "type") == "uml:Stereotype"
                                and e.get("name") == name), name + " stereotype")
                     for name in ("Segment", "Subsystem", "Component", "Facility", "Equipment")}
    block = one((e for e in installed.iter() if e.get(XMI + "type") == "uml:Stereotype"
                 and e.get("name") == "Block"), "installed SysML Block")
    groups = {name: [] for name in EXPECTED}
    untouched = []
    for cls in arch.iter():
        if cls.get(XMI + "type") != "uml:Class":
            continue
        namespace = path(parents[cls])
        require(namespace[:2] == ["Data", "5 - Architecture"], "Unexpected architecture namespace")
        branch = namespace[2:4]
        if namespace[2] in ("L0_Domain", "L1_Mission", "Facilities"):
            group = {"L0_Domain": "domain", "L1_Mission": "mission",
                     "Facilities": "facilities"}[namespace[2]]
        elif branch == ["L2_Segment", "L2.2_Ground Segment"]:
            group = "groundSegment"
        elif branch == ["L3_Subsystems", "L3.2_Ground Subsystems"]:
            group = "groundSubsystems"
        elif branch == ["L4_Components", "L4.2_Ground Subsystems Components"]:
            group = "groundComponents"
        else:
            require(branch in (["L2_Segment", "L2.1_Space Segment"],
                               ["L3_Subsystems", "L3.1_CubeSat Subsystems"],
                               ["L4_Components", "L4.1_CubeSat Subsystems Components"]),
                    f"New architecture branch needs translation: {namespace}")
            untouched.append(cls)
            continue
        groups[group].append(cls)
    require(len(untouched) == 43, "Previously converted CubeSat architecture class count changed")
    require({key: (len(value), sum(len(c.findall("ownedAttribute")) for c in value))
             for key, value in groups.items()} == EXPECTED,
            "Remaining architecture class or property inventory changed")

    class_details = {}
    for group, classes in groups.items():
        for cls in classes:
            require(set(cls.attrib) == {XMI + "type", XMI + "id", "name"} and
                    all(child.tag in ("ownedAttribute", XMI + "Extension") for child in cls) and
                    not cls.findall("generalization") and cls.get("name"),
                    f"Class has additional content to translate: {path(cls)}")
            extensions = [child for child in cls if child.tag == XMI + "Extension"]
            require(all(e.get("extender") == "MagicDraw UML 2024x" for e in extensions),
                    f"Unexpected class extension: {path(cls)}")
            expected_stereotype = {"domain": "Block", "mission": "Block", "groundSegment": "Segment",
                                   "groundSubsystems": "Subsystem", "groundComponents": "Component"}
            stereotype = expected_stereotype.get(group)
            if group == "facilities":
                apps = [a for a in root if a.get("base_Class") == cls.get(XMI + "id")]
                require(len(apps) == 1, f"Unexpected facility stereotype applications: {path(cls)}")
                stereotype = apps[0].tag.rsplit("}", 1)[-1]
                require(stereotype in ("Facility", "Equipment"),
                        f"Unexpected facilities type: {path(cls)}")
            apps = [a for a in root if a.get("base_Class") == cls.get(XMI + "id")]
            require(len(apps) == 1 and apps[0].tag.rsplit("}", 1)[-1] == stereotype and
                    set(apps[0].attrib) == {XMI + "id", "base_Class"},
                    f"Source stereotype needs translation: {path(cls)}")
            stereo_ref = ((SYSML_PROFILE + "#" + block.get(XMI + "id")) if stereotype == "Block"
                          else (PROFILE + "#" + profile_types[stereotype].get(XMI + "id")))
            properties = []
            for prop in cls.findall("ownedAttribute"):
                require(set(prop.attrib) in (
                    {XMI + "type", XMI + "id", "name", "visibility", "aggregation", "type", "association"},
                    {XMI + "type", XMI + "id", "visibility", "aggregation", "type", "association"}) and
                    prop.get(XMI + "type") == "uml:Property" and prop.get("visibility") == "public" and
                    prop.get("aggregation") == "composite" and len(prop) == 0,
                    f"Source property needs a separate translation: {path(cls)}::{prop.get('name')}")
                target = ids.get(prop.get("type"))
                require(target is not None and target.get(XMI + "type") == "uml:Class" and
                        target in [e for e in arch.iter() if e.get(XMI + "type") == "uml:Class"],
                        f"Unconverted source property type: {path(cls)}::{prop.get('name')}")
                assoc = ids.get(prop.get("association"))
                require(assoc is not None and assoc.get(XMI + "type") == "uml:Association" and
                        [e.get(XMI + "idref") for e in assoc.findall("memberEnd")][:1] ==
                        [prop.get(XMI + "id")] and len(assoc.findall("memberEnd")) == 2 and
                        len(assoc.findall("ownedEnd")) == 1 and
                        assoc.find("ownedEnd").get("type") == cls.get(XMI + "id") and
                        assoc.find("ownedEnd").get("association") == prop.get("association") and
                        len([a for a in root if a.tag.rsplit("}", 1)[-1] == "PartProperty"
                             and a.get("base_Property") == prop.get(XMI + "id")]) == 1,
                        f"Unexpected part association or stereotype: {path(cls)}::{prop.get('name')}")
                properties.append({"name": prop.get("name"), "sourceRef": ref(prop),
                                   "associationRef": SOURCE + "#" + prop.get("association"),
                                   "typeRef": ref(target), "typePath": path(target),
                                   "sourceMultiplicity": "1..1"})
            class_details[cls] = {"sourceRef": ref(cls), "path": path(cls),
                                  "stereotypeRef": stereo_ref, "properties": properties}

    def emit_group(classes, start):
        tree = package_tree()
        for cls in classes:
            info = class_details[cls]
            node = tree
            for name in info["path"][start:-1]:
                node = node["packages"].setdefault(name, package_tree())
            node["classes"].append(info)
        lines = []

        def visit(node, level):
            prefix = "    " * level
            for name, child in node["packages"].items():
                lines.append(prefix + "package " + quote(name) + " {")
                visit(child, level + 1)
                lines.append(prefix + "}")
            for info in node["classes"]:
                lines.extend([prefix + "part def " + quote(info["path"][-1]) + " {",
                              prefix + "    @CSRMv1Metadata::ConvertedClassSource {",
                              prefix + "        sourceRef = " + json.dumps(info["sourceRef"]) + ";",
                              prefix + "        stereotypeRef = " + json.dumps(info["stereotypeRef"]) + ";",
                              prefix + '        sourceSummary = "";',
                              prefix + '        sourceId = "";',
                              prefix + "    }"])
                for prop in info["properties"]:
                    declared_type = "::".join(quote(s) for s in prop["typePath"])
                    named = " " + quote(prop["name"]) if prop["name"] is not None else ""
                    lines.extend([prefix + "    part" + named + " : " + declared_type + " [1..1] {",
                                  prefix + "        @CSRMv1Metadata::ConvertedPartSource {",
                                  prefix + "            sourceRef = " + json.dumps(prop["sourceRef"]) + ";",
                                  prefix + "            associationRef = " + json.dumps(prop["associationRef"]) + ";",
                                  prefix + "            sourceTypeRef = " + json.dumps(prop["typeRef"]) + ";",
                                  prefix + '            sourceMultiplicity = "1..1";',
                                  prefix + "        }",
                                  prefix + "    }"])
                lines.append(prefix + "}")

        visit(tree, 2)
        return lines

    branches = {
        "L0_Domain": emit_group(groups["domain"], 2),
        "L1_Mission": emit_group(groups["mission"], 2),
        "L2_Segment": emit_group(groups["groundSegment"], 3),
        "L3_Subsystems": emit_group(groups["groundSubsystems"], 3),
        "L4_Components": emit_group(groups["groundComponents"], 3),
        "Facilities": emit_group(groups["facilities"], 2),
    }
    digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
    output = Path(__file__).resolve().parent
    (output / "architecture-remainder.fragment.json").write_text(json.dumps({
        "sourceArchive": SOURCE, "sourceArchiveSha256": digest, "branches": branches,
    }, indent=2) + "\n")
    audit = {"sourceArchive": SOURCE, "sourceArchiveSha256": digest,
             "sourceInspection": "XMI only; no Cameo validation or simulation run",
             "interpretation": "Direct composite parts with source multiplicities; no ground or facility mass rollup added",
             "previouslyConvertedArchitectureClasses": len(untouched),
             "groups": {key: [class_details[cls] for cls in classes] for key, classes in groups.items()}}
    (output / "architecture-remainder-source-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print("Converted 53 remaining architecture classes and 51 composite properties")


if __name__ == "__main__":
    main()
