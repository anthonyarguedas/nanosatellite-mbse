#!/usr/bin/env python3
"""Convert 2025 Cameo editor customizations to native SysML v2 items.

Usage: python3 convert_cameo_customizations.py DISTROTEMP

These sixteen customizations configure the Cameo editor, not the physical
system. Preserve source fields as typed configuration items. Their targets stay
source references until the matching CSRM profile stereotypes are converted.
Unqualified metadata usages would annotate the containing package by default.
This script does not translate the five derived-property customization classes.
Run before convert_unit_imports.py.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
SOURCE = "CSRM - 2025-11-18.mdzip"
STEREOTYPE_TAG = "{http://www.magicdraw.com/schemas/DSL_Customization.xmi}Customization"
FIELDS = ("customizationTarget", "quickApplyingFor", "preferredMetatype", "superTypes",
          "typesForSource", "typesForTarget", "hiddenOwnedTypes")


def only(items, description):
    items = list(items)
    if len(items) != 1:
        raise ValueError(f"Expected one {description}, found {len(items)}")
    return items[0]


def check(condition, description):
    if not condition:
        raise ValueError(description)


def quote(name):
    check(name and "'" not in name and "\n" not in name and "\r" not in name,
          f"Source identifier needs escaping: {name!r}")
    return "'" + name + "'"


def sequence(items):
    return "(" + ", ".join(json.dumps(item) for item in items) + ")"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    with ZipFile(Path(sys.argv[1]) / SOURCE) as archive:
        root = ET.fromstring(archive.read("com.nomagic.magicdraw.uml_model.model"))
    data = only((e for e in root if e.get("name") == "Data" and
                 e.get(XMI + "type") == "uml:Model"), "source Data model")
    extensions = only((e for e in data if e.get("name") == "CSRM Extentions" and
                       e.get(XMI + "type") == "uml:Package"), "CSRM Extentions package")
    customizations = only((e for e in extensions if e.get("name") == "Customizations" and
                           e.get(XMI + "type") == "uml:Package"), "Customizations package")
    classes = [e for e in customizations if e.get(XMI + "type") == "uml:Class"]
    other = [e for e in customizations if e.get(XMI + "type") != "uml:Class" and
             e.tag != XMI + "Extension"]
    check(len(classes) == 16 and len(other) == 1 and
          other[0].get(XMI + "type") == "uml:Package" and
          other[0].get("name") == "ValidationVerification" and len(other[0]) == 0,
          "Unexpected customizations package contents")
    apps = {e.get("base_Class"): e for e in root if e.tag == STEREOTYPE_TAG and e.get("base_Class")}
    check(len(apps) == 21, "Unexpected number of core Cameo Customization applications")
    report = []
    lines = ["            // Cameo editor configuration. Values are source references, not executable rules."]
    for cls in classes:
        name = cls.get("name")
        ident = cls.get(XMI + "id")
        check(cls.get(XMI + "type") == "uml:Class" and name and ident and
              set(cls.attrib) == {XMI + "type", XMI + "id", "name"} and
              all(child.get(XMI + "type") == "uml:Comment" for child in cls) and
              len(cls.findall("ownedComment")) <= 1,
              f"Additional class content needs translation: {name}")
        comment = cls.find("ownedComment")
        if comment is not None:
            check(comment.get("body") == "Working" and
                  [e.get(XMI + "idref") for e in comment.findall("annotatedElement")] == [ident],
                  f"Unexpected comment on {name}")
        app = apps.get(ident)
        check(app is not None and set(app.attrib) <= {XMI + "id", "base_Class", "hideMetatype"},
              f"Unexpected Customization application: {name}")
        hidden = app.get("hideMetatype")
        check(hidden in (None, "true", "false") and app.get(XMI + "id"),
              f"Unexpected hideMetatype value: {name}")
        values = {}
        for child in app:
            field = child.tag.rsplit("}", 1)[-1]
            check(field in FIELDS and set(child.attrib) == {"href"} and child.get("href") and
                  not list(child), f"Unsupported Cameo customization field: {name}::{field}")
            values.setdefault(field, []).append(child.get("href"))
        check(values.get("customizationTarget"), f"Missing customization target: {name}")
        check(not [a for a in root if a.get("base_Class") == ident and a is not app],
              f"Additional source stereotype on {name}")
        entry = {"name": name, "classRef": SOURCE + "#" + ident,
                 "applicationRef": SOURCE + "#" + app.get(XMI + "id"),
                 "comment": comment.get("body") if comment is not None else "",
                 "hideMetatype": hidden, "fields": values}
        report.append(entry)
        lines.extend(["            item " + quote(name) + " : CSRMCameoCustomization::EditorCustomization {",
                      "                :>> sourceClassRef = " + json.dumps(entry["classRef"]) + ";",
                      "                :>> sourceApplicationRef = " + json.dumps(entry["applicationRef"]) + ";"])
        for field in FIELDS:
            lines.append("                :>> " + field + " = " + sequence(values.get(field, [])) + ";")
        if hidden is not None:
            lines.append("                :>> hideMetatype = " + hidden + ";")
        if comment is not None:
            lines.append("                :>> sourceComment = " + json.dumps(comment.get("body")) + ";")
        lines.append("            }")
    lines.append("            package ValidationVerification;")
    check(len({entry["classRef"] for entry in report}) == 16 and
          sum(len(entry["fields"].get("customizationTarget", [])) for entry in report) == 18,
          "Unexpected source customization identities or targets")
    metadata = [
        "// Native SysML v2 item type for 2025 Cameo editor settings.",
        "// Href values retain source identity. They do not assert native profile typing.",
        "package CSRMCameoCustomization {",
        "    item def EditorCustomization {",
        "        attribute sourceClassRef : ScalarValues::String;",
        "        attribute sourceApplicationRef : ScalarValues::String;",
    ]
    for field in FIELDS:
        metadata.append("        attribute " + field + " : ScalarValues::String [0..*];")
    metadata.extend(["        attribute hideMetatype : ScalarValues::Boolean [0..1];",
                     "        attribute sourceComment : ScalarValues::String [0..1];",
                     "    }", "}"])
    out = Path(__file__).resolve().parent
    (out / "cameo-customizations.sysml").write_text("\n".join(metadata) + "\n")
    (out / "cameo-customizations.fragment").write_text("\n".join(lines) + "\n")
    (out / "cameo-customizations-source-audit.json").write_text(json.dumps({
        "sourceArchive": SOURCE, "sourceInspection": "XMI only; no Cameo execution run",
        "interpretation": "Native items for editor configuration, no runtime behavior asserted",
        "fieldCounts": dict(Counter(field for entry in report for field, refs in entry["fields"].items()
                                    for _ in refs)), "customizations": report,
    }, indent=2) + "\n")
    print("Converted 16 Cameo editor customizations to native item usages")


if __name__ == "__main__":
    main()
