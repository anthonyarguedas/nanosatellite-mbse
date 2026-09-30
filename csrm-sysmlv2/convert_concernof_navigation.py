#!/usr/bin/env python3
"""Translate two direct ConcernOf navigations to native SysML v2 calculations.

Usage: python3 convert_concernof_navigation.py DISTROTEMP

Run audit_derived_properties.py first. The source has zero ConcernOf links.
Inputs remain unbound and are explicitly restricted by contract to outgoing
ConcernOf dependencies with the annotated model element as client. This script
does not fabricate stakeholders or decide the other vendor navigations.
"""

import hashlib
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SOURCE = "CSRM - 2025-11-18.mdzip"
PROFILE = "CSRM-Profile2.mdzip"
XMI = "{http://www.omg.org/spec/XMI/20131001}"
CONCERN_ID = "_19_0_3_2b0010b_1619643905008_952641_430"
UI_FIELDS = ("showGroupInDependencyMatrix", "showGroupInElementSpecification", "showGroupInGoTo",
             "showGroupInQuickProperties", "showGroupInRelationMap", "useAsNode")


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def one(elements, description):
    elements = list(elements)
    ensure(len(elements) == 1, f"Expected one {description}, found {len(elements)}")
    return elements[0]


def quote(name):
    ensure(name and "'" not in name and "\n" not in name and "\r" not in name,
           f"Source name requires escaping: {name!r}")
    return "'" + name + "'"


def annotation(kind, values, level):
    prefix = "    " * level
    return [prefix + "@CSRMRelationshipNavigation::" + kind + " {"] + [
        prefix + "    " + key + " = " + json.dumps(value) + ";"
        for key, value in values.items()
    ] + [prefix + "}"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    src = Path(sys.argv[1])
    out = Path(__file__).resolve().parent
    audit = json.loads((out / "derived-property-source-audit.json").read_text())
    ensure(audit["sourceArchive"] == SOURCE and
           audit["sourceArchiveSha256"] == hashlib.sha256((src / SOURCE).read_bytes()).hexdigest(),
           "Regenerate the derived property source audit for this archive")
    with ZipFile(src / SOURCE) as archive:
        model = ET.fromstring(archive.read("com.nomagic.magicdraw.uml_model.model"))
    with ZipFile(src / PROFILE) as archive:
        profile = ET.fromstring(archive.read("com.nomagic.magicdraw.uml_model.shared_model"))
    relation = one((e for e in profile.iter() if e.get(XMI + "id") == CONCERN_ID), "ConcernOf stereotype")
    base = one((e for e in relation.findall("ownedAttribute") if e.get("name") == "base_Dependency"),
               "ConcernOf base Dependency")
    comment = one(relation.findall("ownedComment"), "ConcernOf description").get("body") or ""
    ensure(relation.get(XMI + "type") == "uml:Stereotype" and relation.get("name") == "ConcernOf" and
           base.find("type") is not None and
           base.find("type").get("href") == "http://www.omg.org/spec/UML/20131001/UML.xmi#Dependency" and
           "The client of the dependency can be any element" in comment and
           "supplier must be a type of «Stakeholder»" in comment,
           "Source ConcernOf endpoint semantics changed")
    applications = [a for a in model if a.tag.rsplit("}", 1)[-1] == "ConcernOf" and
                    a.get("base_Dependency")]
    ensure(not applications, "Source ConcernOf relationships need native endpoints and bindings")
    class_records = []
    for name, target_name, total in (("Group Customization", "Group", 2),
                                     ("StakeholderConcern Customization", "StakeholderConcern", 4)):
        cls = one((c for c in audit["classes"] if c["name"] == name), name)
        ensure(len(cls["customizationTargetRefs"]) == 1 and len(cls["properties"]) == total,
               f"{name} target or source property count changed")
        target_ref = cls["customizationTargetRefs"][0]
        ensure(target_ref.startswith(PROFILE + "#"), f"{name} target is not the attached profile")
        target = one((e for e in profile.iter() if e.get(XMI + "id") == target_ref.split("#", 1)[1]),
                     f"{name} target stereotype")
        ensure(target.get(XMI + "type") == "uml:Stereotype" and target.get("name") == target_name,
               f"{name} customization target changed")
        derived = one((p for p in cls["properties"] if p["name"] == "Stakeholders" and
                       p["kind"] == "derivedPropertySpecification"), name + " Stakeholders")
        group = one((p for p in cls["properties"] if p["name"] == "Traceability" and
                     p["kind"] == "propertyGroup"), name + " Traceability")
        expr = derived["expression"]
        ensure(expr["kind"] == "callExpressionSpecification" and
               expr["attributes"] == {"includeCustomTypes": "true", "includeSubtypes": "false"} and
               [c["kind"] for c in expr["children"]] == ["taggedValues", "argument", "expression"] and
               expr["children"][1]["attributes"] == {"type": "lookupExpressionSpecification", "symbol": "THIS"} and
               expr["children"][0]["children"][0]["children"][0]["text"] == "ConcernOf" and
               expr["children"][2]["attributes"] == {
                   "type": "dslRelationExpressionSpecification", "stereotype": CONCERN_ID,
                   "direction": "DIRECT", "includeCustomTypes": "true", "includeSubtypes": "true"} and
               derived["typeRef"] == "http://www.omg.org/spec/UML/20131001/UML.xmi#Element" and
               derived["visibility"] == "private", f"{name} ConcernOf expression changed")
        ensure(group["visibility"] == "private" and set(group["presentationFields"]) == set(UI_FIELDS) and
               all(v == "true" for v in group["presentationFields"].values()) and
               len(group["qualifiers"]) == 1 and group["qualifiers"][0]["name"] == "Other" and
               not group["qualifiers"][0]["typeRef"], f"{name} property group changed")
        class_records.append((cls, derived, group, target_ref))

    src_relation = PROFILE + "#" + CONCERN_ID
    common = [
        "// Source-scoped direct ConcernOf navigation. No 2025 ConcernOf links exist.",
        "package CSRMRelationshipNavigation {",
        "    metadata def CustomizationSource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute sourceTargetRef : ScalarValues::String;",
        "        attribute convertedOwnedProperties : ScalarValues::Integer;",
        "    }",
        "    metadata def SourceRelationshipInput {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute sourceCustomizationRef : ScalarValues::String;",
        "        attribute sourceTargetStereotypeRef : ScalarValues::String;",
        "        attribute relationKind : ScalarValues::String;",
        "        attribute direction : ScalarValues::String;",
        "        attribute sourceLinkCount : ScalarValues::Integer;",
        "        attribute isSourceFeature : ScalarValues::Boolean;",
        "        attribute bindingContract : ScalarValues::String;",
        "    }",
        "    metadata def DerivedPropertySource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute sourceTypeRef : ScalarValues::String;",
        "        attribute sourceRelationRef : ScalarValues::String;",
        "        attribute sourceDirection : ScalarValues::String;",
        "    }",
        "    metadata def PropertyGroupSource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute qualifierRef : ScalarValues::String;",
        "        attribute qualifierName : ScalarValues::String;",
    ]
    common += ["        attribute " + name + " : ScalarValues::Boolean;" for name in UI_FIELDS]
    common += ["    }", "    calc def ConcernOfSuppliers {"]
    common += annotation("DerivedPropertySource", {
        "sourceRef": class_records[0][1]["sourceRef"],
        "applicationRef": class_records[0][1]["applicationRef"],
        "sourceTypeRef": class_records[0][1]["typeRef"],
        "sourceRelationRef": src_relation, "sourceDirection": "DIRECT",
    }, 2)
    common += ["        in ref directConcernOfLinks : KerML::Dependency [0..*];",
               "        return ref stakeholders : KerML::Element [0..*];",
               "        directConcernOfLinks.supplier", "    }", "}"]

    fragment = ["            // Customization definitions with native direct ConcernOf navigation."]
    for cls, derived, group, target_ref in class_records:
        prefix = "            "
        fragment += [prefix + "item def " + quote(cls["name"]) + " {"]
        fragment += annotation("CustomizationSource", {
            "sourceRef": cls["sourceRef"], "applicationRef": cls["applicationRef"],
            "sourceTargetRef": target_ref, "convertedOwnedProperties": 2,
        }, 4)
        fragment += [prefix + "    // Filtered native input, unbound because no source ConcernOf link exists.",
                     prefix + "    ref directConcernOfLinks : KerML::Dependency [0..*] {"]
        fragment += annotation("SourceRelationshipInput", {
            "sourceRef": src_relation, "sourceCustomizationRef": cls["sourceRef"],
            "sourceTargetStereotypeRef": target_ref,
            "relationKind": "ConcernOf", "direction": "DIRECT", "sourceLinkCount": 0,
            "isSourceFeature": False,
            "bindingContract": "Only ConcernOf dependencies with this customization target element as client and a Stakeholder supplier",
        }, 5)
        fragment += [prefix + "    }",
                     prefix + "    private derived ref Stakeholders : KerML::Element [0..*] = " +
                     "CSRMRelationshipNavigation::ConcernOfSuppliers(directConcernOfLinks) {"]
        fragment += annotation("DerivedPropertySource", {
            "sourceRef": derived["sourceRef"], "applicationRef": derived["applicationRef"],
            "sourceTypeRef": derived["typeRef"], "sourceRelationRef": src_relation,
            "sourceDirection": "DIRECT",
        }, 5)
        fragment += [prefix + "    }",
                     prefix + "    private metadata Traceability : CSRMRelationshipNavigation::PropertyGroupSource {"]
        values = {
            "sourceRef": group["sourceRef"], "applicationRef": group["applicationRef"],
            "qualifierRef": group["qualifiers"][0]["sourceRef"],
            "qualifierName": group["qualifiers"][0]["name"],
        }
        fragment += [prefix + "        " + k + " = " + json.dumps(v) + ";" for k, v in values.items()]
        fragment += [prefix + "        " + k + " = true;" for k in UI_FIELDS]
        fragment += [prefix + "    }", prefix + "}"]

    (out / "concernof-navigation.sysml").write_text("\n".join(common) + "\n")
    (out / "concernof-navigation.fragment").write_text("\n".join(fragment) + "\n")
    (out / "concernof-navigation-source-audit.json").write_text(json.dumps({
        "sourceArchive": SOURCE, "sourceArchiveSha256": audit["sourceArchiveSha256"],
        "profileRelationRef": src_relation, "sourceRelationKind": "UML Dependency stereotype",
        "clientRule": "any model element", "supplierRule": "Stakeholder stereotype",
        "sourceConcernOfApplicationCount": 0,
        "navigation": "DIRECT: selected ConcernOf dependencies.supplier",
        "nativeInput": "unbound KerML::Dependency [0..*]; only dependencies with THIS as client and Stakeholder supplier",
        "sourceClassRefs": [c[0]["sourceRef"] for c in class_records],
        "sourceTargetRefs": [c[3] for c in class_records],
        "sourcePropertyRefs": [c[1]["sourceRef"] for c in class_records],
        "sourceGroupRefs": [c[2]["sourceRef"] for c in class_records],
        "deferredStakeholderConcernProperties": [p["sourceRef"] for p in class_records[1][0]["properties"]
                                                if p["name"] not in ("Stakeholders", "Traceability")],
        "cameoExpressionExecution": "not run", "nativeCalculationEvaluation": "not run",
    }, indent=2) + "\n")
    print("Converted two ConcernOf navigations; zero source links, no native input binding")


if __name__ == "__main__":
    main()
