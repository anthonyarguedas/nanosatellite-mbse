#!/usr/bin/env python3
"""Translate the two Duplicate Customization metachains using a native input.

Usage: python3 convert_duplicate_navigation.py DISTROTEMP

Run audit_derived_properties.py first. The vendor Duplicate::ownedElement tag
is unavailable. The user authorized a native reflective KerML::Element input
in its place. The two results navigate its KerML owner and qualifiedName.
The input is unbound because the source has no Duplicate customization target
or owned-element instances. No Cameo expression is evaluated here.
"""

import hashlib
import json
import sys
from pathlib import Path

SOURCE = "CSRM - 2025-11-18.mdzip"
CHAIN = {"type": "stereotypeProperty", "profile": "Problem extensions",
         "stereotype": "Duplicate", "tag": "ownedElement", "derived": "true"}
GROUP_FIELDS = ("showGroupInDependencyMatrix", "showGroupInElementSpecification",
                "showGroupInGoTo", "showGroupInQuickProperties", "showGroupInRelationMap", "useAsNode")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def one(items, label):
    items = list(items)
    require(len(items) == 1, f"Expected one {label}, found {len(items)}")
    return items[0]


def quote(name):
    require(name and "'" not in name and "\n" not in name and "\r" not in name,
            f"Identifier requires escaping: {name!r}")
    return "'" + name + "'"


def field(key, value, indent=12):
    return " " * indent + key + " = " + json.dumps(value) + ";"


def metadata(name, values, indent=8):
    prefix = " " * indent
    return [prefix + "@CSRMDuplicateNavigation::" + name + " {"] + [
        field(k, v, indent + 4) for k, v in values.items()
    ] + [prefix + "}"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = Path(__file__).resolve().parent
    audit = json.loads((out / "derived-property-source-audit.json").read_text())
    source_file = Path(sys.argv[1]) / SOURCE
    require(audit["sourceArchive"] == SOURCE and
            audit["sourceArchiveSha256"] == hashlib.sha256(source_file.read_bytes()).hexdigest(),
            "Regenerate the derived property XMI audit for this archive")
    cls = one((c for c in audit["classes"] if c["name"] == "Duplicate Customization"),
              "Duplicate Customization class")
    require(not cls["customizationTargetRefs"] and len(cls["properties"]) == 3 and
            cls["sourceRef"] == SOURCE + "#_19_0_3_2b0010b_1613836106767_154950_10738",
            "Duplicate class or missing source target changed")
    derived = [p for p in cls["properties"] if p["kind"] == "derivedPropertySpecification"]
    group = one((p for p in cls["properties"] if p["kind"] == "propertyGroup"),
                "Traceability property group")
    require([p["name"] for p in derived] == ["Duplicated Element", "Qualified Named of Duplicate"] and
            group["name"] == "Traceability" and
            set(group["presentationFields"]) == set(GROUP_FIELDS) and
            all(v == "true" for v in group["presentationFields"].values()) and
            len(group["qualifiers"]) == 1 and
            group["qualifiers"][0]["name"] == "Other" and
            not group["qualifiers"][0]["typeRef"],
            "Source derived properties or presentation settings changed")
    kinds = []
    for prop in derived:
        expr = prop["expression"]
        require(expr["kind"] == "callExpressionSpecification" and
                expr["attributes"] == {"includeCustomTypes": "true", "includeSubtypes": "false"} and
                [child["kind"] for child in expr["children"]] ==
                ["taggedValues", "argument", "expression"] and
                expr["children"][1]["attributes"] ==
                {"type": "lookupExpressionSpecification", "symbol": "THIS"},
                "Source call expression changed")
        chain = expr["children"][2]
        require(chain["attributes"] == {"type": "metaChainExpressionSpecification",
                                          "ordered": "true", "unique": "true",
                                          "includeCustomTypes": "true", "includeSubtypes": "true"} and
                all(n["kind"] == "chain" and not n["children"] for n in chain["children"]),
                "Source chain ordering or navigation changed")
        kinds.append([c["attributes"] for c in chain["children"]])
    require(kinds == [
        [CHAIN, {"type": "umlProperty", "metaclass": "Element", "property": "owner"}],
        [CHAIN, {"type": "umlProperty", "metaclass": "NamedElement", "property": "owner"},
         {"type": "umlProperty", "metaclass": "NamedElement", "property": "qualifiedName"}],
    ] and derived[0]["typeRef"] == "http://www.omg.org/spec/UML/20131001/UML.xmi#Element" and
            derived[1]["typeRef"] == "http://www.omg.org/spec/UML/20131001/PrimitiveTypes.xmi#String" and
            all(p["visibility"] == "private" for p in cls["properties"]),
            "Source type, visibility, or metachain needs another decision")
    common = [
        "// Native owner navigation for the source Duplicate customization.",
        "// The missing vendor Duplicate::ownedElement is an unbound reflective input.",
        "package CSRMDuplicateNavigation {",
        "    metadata def CustomizationSource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute sourceHadTarget : ScalarValues::Boolean;",
        "    }",
        "    metadata def ChosenOwnedElementInput {",
        "        attribute sourceClassRef : ScalarValues::String;",
        "        attribute vendorProfile : ScalarValues::String;",
        "        attribute vendorStereotype : ScalarValues::String;",
        "        attribute vendorTag : ScalarValues::String;",
        "        attribute isSourceFeature : ScalarValues::Boolean;",
        "        attribute interpretation : ScalarValues::String;",
        "    }",
        "    metadata def DerivedPropertySource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute sourceTypeRef : ScalarValues::String;",
        "        attribute sourceNavigation : ScalarValues::String;",
        "    }",
        "    metadata def PropertyGroupSource {",
        "        attribute sourceRef : ScalarValues::String;",
        "        attribute applicationRef : ScalarValues::String;",
        "        attribute qualifierRef : ScalarValues::String;",
        "        attribute qualifierName : ScalarValues::String;",
    ]
    common += ["        attribute " + name + " : ScalarValues::Boolean;" for name in GROUP_FIELDS]
    common += ["    }", "    calc def DuplicateOwners {"]
    common += metadata("DerivedPropertySource", {
        "sourceRef": derived[0]["sourceRef"], "applicationRef": derived[0]["applicationRef"],
        "sourceTypeRef": derived[0]["typeRef"],
        "sourceNavigation": "Duplicate.ownedElement.owner",
    }, indent=8)
    common += ["        in ref ownedElements : KerML::Element [0..*] ordered;",
               "        return ref owners : KerML::Element [0..*] ordered;",
               "        ownedElements.owner", "    }", "    calc def DuplicateOwnerQualifiedNames {"]
    common += metadata("DerivedPropertySource", {
        "sourceRef": derived[1]["sourceRef"], "applicationRef": derived[1]["applicationRef"],
        "sourceTypeRef": derived[1]["typeRef"],
        "sourceNavigation": "Duplicate.ownedElement.owner.qualifiedName",
    }, indent=8)
    common += ["        in ref ownedElements : KerML::Element [0..*] ordered;",
               "        return attribute names : ScalarValues::String [0..*] ordered;",
               "        ownedElements.owner.qualifiedName", "    }", "}"]

    prefix = "            "
    fragment = ["    package 'Derived Properties' {",
                prefix + "item def 'Duplicate Customization' {"]
    fragment += metadata("CustomizationSource", {
        "sourceRef": cls["sourceRef"], "applicationRef": cls["applicationRef"],
        "sourceHadTarget": False,
    }, indent=16)
    fragment += [prefix + "    // Chosen native input replaces the unavailable vendor-derived tag.",
                 prefix + "    ref duplicateOwnedElement : KerML::Element [0..*] ordered {"]
    fragment += metadata("ChosenOwnedElementInput", {
        "sourceClassRef": cls["sourceRef"], "vendorProfile": CHAIN["profile"],
        "vendorStereotype": CHAIN["stereotype"], "vendorTag": CHAIN["tag"],
        "isSourceFeature": False,
        "interpretation": "User-authorized unbound reflective input; no source Duplicate target or instances",
    }, indent=20)
    fragment += [prefix + "    }"]
    specs = [
        (derived[0], "ref", "KerML::Element", "DuplicateOwners", "Duplicate.ownedElement.owner"),
        (derived[1], "attribute", "ScalarValues::String", "DuplicateOwnerQualifiedNames",
         "Duplicate.ownedElement.owner.qualifiedName"),
    ]
    for prop, kind, typ, calc, navigation in specs:
        fragment += [prefix + f"    private derived {kind} {quote(prop['name'])} : {typ} [0..*] ordered = " +
                     "CSRMDuplicateNavigation::" + calc + "(duplicateOwnedElement) {"]
        fragment += metadata("DerivedPropertySource", {
            "sourceRef": prop["sourceRef"], "applicationRef": prop["applicationRef"],
            "sourceTypeRef": prop["typeRef"], "sourceNavigation": navigation,
        }, indent=20)
        fragment += [prefix + "    }"]
    fragment += [prefix + "    private metadata 'Traceability' : CSRMDuplicateNavigation::PropertyGroupSource {"]
    fragment += [field("sourceRef", group["sourceRef"], 20),
                 field("applicationRef", group["applicationRef"], 20),
                 field("qualifierRef", group["qualifiers"][0]["sourceRef"], 20),
                 field("qualifierName", group["qualifiers"][0]["name"], 20)]
    fragment += ["                    " + name + " = true;" for name in GROUP_FIELDS]
    fragment += [prefix + "    }", prefix + "}", "    }"]
    (out / "duplicate-navigation.sysml").write_text("\n".join(common) + "\n")
    (out / "duplicate-navigation.fragment").write_text("\n".join(fragment) + "\n")
    (out / "duplicate-navigation-source-audit.json").write_text(json.dumps({
        "sourceArchive": SOURCE, "sourceArchiveSha256": audit["sourceArchiveSha256"],
        "sourceClassRef": cls["sourceRef"], "sourceClassApplicationRef": cls["applicationRef"],
        "sourceCustomizationTargetRefs": cls["customizationTargetRefs"],
        "sourceDerivedPropertyRefs": [p["sourceRef"] for p in derived],
        "sourceDerivedPropertyApplicationRefs": [p["applicationRef"] for p in derived],
        "sourceGroupRef": group["sourceRef"],
        "vendorTag": CHAIN, "sourceMetachains": kinds,
        "choice": "user-authorized native unbound reflective KerML::Element input in place of missing Duplicate.ownedElement",
        "ownerSemantics": "KerML::Element::owner and qualifiedName (KerML v1.0, PDF pp. 135-139)",
        "cameoExpressionExecution": "not run", "nativeCalculationEvaluation": "not run",
        "inputBinding": "none; 2025 source has no Duplicate customization target or owned-element instances",
    }, indent=2) + "\n")
    print("Converted Duplicate Customization and two source metachains using a native reflective input")


if __name__ == "__main__":
    main()
