#!/usr/bin/env python3
"""Inventory vendor expressions before translating the 2025 derived properties.

Usage: python3 audit_derived_properties.py DISTROTEMP

Source inspection only. Does not evaluate expressions or generate SysML v2
properties. convert_duplicate_navigation.py translates the two Duplicate chains
using a user-authorized native input in place of the missing vendor relation.
"""

import hashlib
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
SOURCE = "CSRM - 2025-11-18.mdzip"


def only(elements, description):
    elements = list(elements)
    if len(elements) != 1:
        raise ValueError(f"Expected one {description}, found {len(elements)}")
    return elements[0]


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def node(element):
    return {"kind": local(element),
            "attributes": {key.rsplit("}", 1)[-1]: value for key, value in element.attrib.items()},
            "text": (element.text or "").strip(),
            "children": [node(child) for child in element]}


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source_file = Path(sys.argv[1]) / SOURCE
    with ZipFile(source_file) as archive:
        root = ET.fromstring(archive.read("com.nomagic.magicdraw.uml_model.model"))
    data = only((e for e in root if e.get("name") == "Data"), "Data model")
    package = only((e for e in data if e.get("name") == "Derived Properties"), "derived properties")
    classes = [e for e in package if e.get(XMI + "type") == "uml:Class"]
    if len(classes) != 5:
        raise ValueError("Derived property class count changed")
    apps = {}
    for e in root:
        if e.get("base_Property"):
            apps.setdefault(e.get("base_Property"), []).append(e)
    records = []
    for cls in classes:
        cls_id = cls.get(XMI + "id")
        class_app = only((a for a in root if a.get("base_Class") == cls_id),
                         f"{cls.get('name')} stereotype")
        if local(class_app) != "Customization":
            raise ValueError("Unexpected derived property class stereotype")
        targets = [a.get("href") for a in class_app if local(a) == "customizationTarget"]
        if len(targets) != len(class_app):
            raise ValueError("Other customization fields need inspection")
        props = []
        for prop in cls.findall("ownedAttribute"):
            prop_id = prop.get(XMI + "id")
            app = only(apps.get(prop_id, []), "derived property or property group application")
            item = {"name": prop.get("name"), "sourceRef": SOURCE + "#" + prop_id,
                    "applicationRef": SOURCE + "#" + app.get(XMI + "id"),
                    "typeRef": prop.get("type") or (prop.find("type").get("href") if prop.find("type") is not None else ""),
                    "visibility": prop.get("visibility"), "kind": local(app)}
            if local(app) == "derivedPropertySpecification":
                expression = ET.fromstring(only(app.findall("expression"), "derived expression").text)
                if local(expression) != "callExpressionSpecification":
                    raise ValueError("New vendor expression kind needs inspection")
                item["expression"] = node(expression)
                item["parsedExpressionXml"] = ET.tostring(expression, encoding="unicode")
            elif local(app) == "propertyGroup":
                item["presentationFields"] = {key: value for key, value in app.attrib.items()
                                              if key not in (XMI + "id", "base_Property")}
                item["qualifiers"] = [{"sourceRef": SOURCE + "#" + p.get(XMI + "id"),
                                       "name": p.get("name"), "typeRef": p.get("type") or ""}
                                      for p in prop.findall("qualifier")]
            else:
                raise ValueError("New derived property application needs inspection")
            props.append(item)
        records.append({"name": cls.get("name"), "sourceRef": SOURCE + "#" + cls_id,
                        "applicationRef": SOURCE + "#" + class_app.get(XMI + "id"),
                        "customizationTargetRefs": targets, "properties": props})
    property_records = [prop for cls in records for prop in cls["properties"]]
    if len(property_records) != 13 or [p["kind"] for p in property_records].count(
            "derivedPropertySpecification") != 8 or [p["kind"] for p in property_records].count(
            "propertyGroup") != 5:
        raise ValueError("Derived property inventory changed")
    duplicate = only((cls for cls in records if cls["name"] == "Duplicate Customization"),
                     "Duplicate Customization")
    if duplicate["customizationTargetRefs"]:
        raise ValueError("Duplicate Customization gained a target to translate")
    for prop in duplicate["properties"]:
        if prop["kind"] != "derivedPropertySpecification":
            continue
        chains = [e for e in prop["expression"]["children"] if e["kind"] == "expression"]
        if len(chains) != 1 or not any(c["attributes"].get("profile") == "Problem extensions" and
                                       c["attributes"].get("stereotype") == "Duplicate" and
                                       c["attributes"].get("tag") == "ownedElement"
                                       for c in chains[0]["children"]):
            raise ValueError("Duplicate navigation changed")
    report = {"sourceArchive": SOURCE,
              "sourceArchiveSha256": hashlib.sha256(source_file.read_bytes()).hexdigest(),
              "sourceInspection": "XMI only; Cameo expressions not executed",
              "externalDependency": "Problem extensions::Duplicate::ownedElement is referenced; no external implementation or target is embedded",
              "classes": records}
    dest = Path(__file__).resolve().parent / "derived-property-source-audit.json"
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print("Audited 5 customization classes, 8 vendor-derived properties, and 5 UI property groups")


if __name__ == "__main__":
    main()
