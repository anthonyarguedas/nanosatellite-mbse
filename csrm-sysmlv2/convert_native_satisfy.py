#!/usr/bin/env python3
"""Convert four Satisfy rules to native measure property types and predicates.

Usage: python3 convert_native_satisfy.py DISTROTEMP [SYSML_PROFILE_MDZIP]

Generates model types and an audit. Run before convert_refine_rules.py, which
inserts native-satisfy.fragment into measure-validation.sysml.
"""

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
MAIN = "CSRM - 2025-11-18.mdzip"
PROFILE = "CSRM-Profile2.mdzip"
SYSML_PROFILE = "SysML Profile.mdzip"
SPECS = (
    ("kpp", "KPP", PROFILE, "KPP", "kppRequirement Satisfy & kpp stereotype", "Type Test1(kpp)"),
    ("moe", "MoE", SYSML_PROFILE, "moe", "moeRequirement Satisfy by MoE Param", "Type Test1(MoE)"),
    ("mop", "MoP", PROFILE, "mop", "mopRequirement Satisfy by MoP Param", "Type Test1(MoP)"),
    ("tpm", "TPM", PROFILE, "TPM", "tpmRequirement Satisfy by TPM Param1", "Type Test1(tpm)"),
)


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def read_root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def named_child(parent, name):
    matches = [element for element in parent if element.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one {name!r}, found {len(matches)}")
    return matches[0]


def named_stereotype(root, name):
    matches = [element for element in root.iter() if element.get(XMI + "type") == "uml:Stereotype" and element.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one stereotype {name!r}, found {len(matches)}")
    return matches[0]


def call_names_and_options(expression):
    calls = {}
    for call in expression.iter():
        if call.get(XSI_TYPE) != "callExpressionSpecification":
            continue
        names = ["".join(value.itertext()).strip() for tags in call if local(tags) == "taggedValues"
                 for entry in tags if entry.get("key") == "name" for value in entry]
        for name in names:
            calls[name] = call.attrib
    return calls


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    folder = Path(sys.argv[1])
    sysml_path = Path(sys.argv[2]) if len(sys.argv) == 3 else Path("/Applications/Magic Systems of Systems Architect/profiles") / SYSML_PROFILE
    roots = {
        PROFILE: read_root(folder / PROFILE, "com.nomagic.magicdraw.uml_model.shared_model"),
        SYSML_PROFILE: read_root(sysml_path, "com.nomagic.magicdraw.uml_model.shared_model"),
    }
    root = read_root(folder / MAIN, "com.nomagic.magicdraw.uml_model.model")
    model = named_child(root, "Data")
    rules = named_child(named_child(named_child(model, "CSRM Extentions"), "Model Constraints"), "Measure Validation")
    abstractions = {e.get(XMI + "id"): e for e in root.iter() if e.get(XMI + "type") == "uml:Abstraction"}
    satisfy_ids = [e.get("base_Abstraction") for e in root if local(e) == "Satisfy"]
    type_lines = ["// Native value types for the four source performance property stereotypes.", "package CSRMNativeMeasures {"]
    rule_lines = ["    // These inputs are the Satisfy clients selected by each native measure type."]
    audits = []

    for prefix, type_name, source_archive, stereo_name, rule_name, type_test in SPECS:
        stereotype = named_stereotype(roots[source_archive], stereo_name)
        req_stereotype = named_stereotype(roots[PROFILE], prefix + "Requirement")
        if not any(child.get("name") == "base_Property" for child in stereotype):
            raise ValueError(f"{stereo_name} does not extend UML Property")
        comment = stereotype.find("ownedComment")
        doc = comment.get("body") if comment is not None else ""
        if "*/" in doc:
            raise ValueError(f"Source documentation needs escaping for {stereo_name}")
        rule = named_child(rules, rule_name)
        spec = rule.find("specification")
        if rule.get(XMI + "type") != "uml:Constraint" or spec is None or spec.findtext("language") != "StructuredExpression":
            raise ValueError(f"Unexpected rule representation: {rule_name}")
        scope_ref = PROFILE + "#" + req_stereotype.get(XMI + "id")
        if [item.get("href") for item in rule if item.tag == "constrainedElement"] != [scope_ref]:
            raise ValueError(f"Unexpected requirement scope: {rule_name}")
        expression = ET.fromstring(spec.findtext("body"))
        chains = [e for e in expression.iter() if e.get(XSI_TYPE) == "metaChainExpressionSpecification"]
        path = [(e.get("stereotype"), e.get("tag")) for chain in chains for e in chain if local(e) == "chain"]
        if len(chains) != 1 or path != [(prefix + "Requirement", "_directedRelationshipOfTarget"), ("Satisfy", "source")]:
            raise ValueError(f"Unexpected Satisfy rule navigation: {rule_name}")
        stereotype_id = stereotype.get(XMI + "id")
        if sum(e.get("element") == stereotype_id for e in expression.iter()) != 1:
            raise ValueError(f"Unexpected type test target: {rule_name}")
        calls = call_names_and_options(expression)
        if not {"IsEmpty1", "Filter", "Metachain Navigation1", type_test}.issubset(calls):
            raise ValueError(f"Unexpected rule functions: {rule_name}")
        if calls[type_test].get("includeSubtypes") != "true":
            raise ValueError(f"Unexpected subtype behavior: {rule_name}")

        requirements = [e.get("base_Class") for e in root if local(e) == prefix + "Requirement" and e.get("base_Class")]
        properties = {e.get("base_Property") for e in root if local(e) == stereo_name and e.get("base_Property")}
        subjects = []
        for requirement in requirements:
            matches = []
            for relation_id in satisfy_ids:
                relation = abstractions[relation_id]
                clients = [e.get(XMI + "idref") for e in relation if e.tag == "client"]
                suppliers = [e.get(XMI + "idref") for e in relation if e.tag == "supplier"]
                if requirement in suppliers:
                    matches.extend((relation_id, client) for client in clients if client in properties)
            subjects.append({
                "requirementId": requirement,
                "matchingSatisfyRelations": [ident for ident, _ in matches],
                "matchingNativeProperties": [ident for _, ident in matches],
            })
        if len(subjects) != 2 or properties or any(x["matchingSatisfyRelations"] for x in subjects):
            raise ValueError(f"Matching {type_name} properties require feature conversion")
        audits.append({
            "prefix": prefix,
            "typeName": type_name,
            "rule": rule_name,
            "ruleId": rule.get(XMI + "id"),
            "propertyStereotypeRef": source_archive + "#" + stereotype_id,
            "requirements": subjects,
            "propertyCount": len(properties),
            "sourceSatisfyRelationCount": len(satisfy_ids),
            "cameoRuleExecution": "not run",
        })

        type_lines.extend([
            f"    attribute def {type_name} {{",
            f"        doc /*{doc}*/",
            "        @CSRMv1Metadata::NativePropertyTypeSource {",
            f"            sourceRef = {json.dumps(source_archive + '#' + stereotype_id)};",
            '            sourceKind = "SysML v1 performance Property stereotype";',
            "        }",
            "    }",
        ])
        parameter = f"matching{type_name}Satisfiers" if type_name != "KPP" else "matchingKppSatisfiers"
        rule_lines.extend([
            f"    constraint def '{rule_name}' {{",
            "        @CSRMv1Metadata::ValidationRuleSource {",
            f"            sourceRef = {json.dumps(MAIN + '#' + rule.get(XMI + 'id'))};",
            f"            scopeRef = {json.dumps(scope_ref)};",
            f"            targetRef = {json.dumps(source_archive + '#' + stereotype_id)};",
            f"            relation = {json.dumps('SysML v1 Satisfy: ' + stereo_name + ' Property client to ' + prefix + 'Requirement supplier')};",
            "        }",
            f"        in attribute {parameter} : CSRMNativeMeasures::{type_name} [0..*];",
            f"        SequenceFunctions::size({parameter}) > 0",
            "    }",
        ])
    type_lines.append("}")
    out = Path(__file__).resolve().parent
    (out / "native-measures.sysml").write_text("\n".join(type_lines) + "\n")
    (out / "native-satisfy.fragment").write_text("\n".join(rule_lines) + "\n")
    (out / "satisfy-source-audit.json").write_text(json.dumps(audits, indent=2) + "\n")
    print(f"Generated {len(audits)} native measure types and Satisfy rules with {sum(len(x['requirements']) for x in audits)} subjects")


if __name__ == "__main__":
    main()
