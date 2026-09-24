#!/usr/bin/env python3
"""Translate four Refined predicates, append Satisfy rules, and audit the source.

Usage: python3 convert_refine_rules.py DISTROTEMP

The generated SysML v2 predicates accept matching refinement targets. Binding
those inputs to converted dependencies is separate from defining the predicate.
"""

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
RULE_NAMES = (
    "moeRequirement Refined",
    "mopRequirement Refined",
    "kppRequirement Refined",
    "tpmRequirement Refined",
)
MAIN_ARCHIVE = "CSRM - 2025-11-18.mdzip"
PROFILE_ARCHIVE = "CSRM-Profile2.mdzip"


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def read_model(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def named_child(parent, name):
    matches = [element for element in parent if element.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one {name!r}, found {len(matches)}")
    return matches[0]


def paths_of(root):
    paths = {}

    def walk(element, path):
        path = path + ((element.get("name"),) if element.get("name") else ())
        if element.get(XMI + "id"):
            paths[element.get(XMI + "id")] = "::".join(path)
        for child in element:
            walk(child, path)

    walk(root, ())
    return paths


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source_dir = Path(sys.argv[1])
    root = read_model(source_dir / MAIN_ARCHIVE, "com.nomagic.magicdraw.uml_model.model")
    profile = read_model(source_dir / PROFILE_ARCHIVE, "com.nomagic.magicdraw.uml_model.shared_model")
    ids = {element.get(XMI + "id"): element for element in profile.iter() if element.get(XMI + "id")}
    paths = paths_of(root)
    model = named_child(root, "Data")
    ext = named_child(model, "CSRM Extentions")
    validation = named_child(named_child(ext, "Model Constraints"), "Measure Validation")
    all_rules = {child.get("name"): child for child in validation if child.get(XMI + "type") == "uml:Constraint"}
    if any(name not in all_rules for name in RULE_NAMES):
        raise ValueError("Missing Refined validation rule")

    # Look up the UML abstractions with the SysML v1 Refine stereotype.
    abstractions = {element.get(XMI + "id"): element for element in root.iter() if element.get(XMI + "type") == "uml:Abstraction"}
    refine_ids = {element.get("base_Abstraction") for element in root if local(element) == "Refine"}
    refines = []
    for ident in refine_ids:
        relation = abstractions[ident]
        clients = [item.get(XMI + "idref") for item in relation if item.tag == "client"]
        suppliers = [item.get(XMI + "idref") for item in relation if item.tag == "supplier"]
        if not clients or not suppliers or None in clients + suppliers:
            raise ValueError(f"Unresolved Refine endpoints: {ident}")
        refines.extend((ident, client, supplier) for client in clients for supplier in suppliers)

    output = Path(__file__).resolve().parent
    lines = [
        "// Each constraint receives targets already filtered by the relation and stereotype.",
        "// The Refined rule inputs are bound by asserted usages in model.sysml.",
        "package CSRMMeasureValidation {",
    ]
    report = []
    for name in RULE_NAMES:
        rule = all_rules[name]
        spec = rule.find("specification")
        if spec is None or spec.findtext("language") != "StructuredExpression":
            raise ValueError(f"Unexpected expression language for {name}")
        expression = ET.fromstring(spec.findtext("body"))
        chains = [element for element in expression.iter() if element.get(XSI_TYPE) == "metaChainExpressionSpecification"]
        if len(chains) != 1:
            raise ValueError(f"Unexpected navigation count for {name}")
        path = [(item.get("stereotype"), item.get("tag")) for item in chains[0] if local(item) == "chain"]
        if len(path) != 2 or path[0][1] != "_directedRelationshipOfSource" or path[1] != ("Refine", "target"):
            raise ValueError(f"Unexpected navigation for {name}: {path}")
        type_filters = [element for element in expression.iter() if local(element) == "type" and element.get(XSI_TYPE) == "stereotypeIdType"]
        scope = [element.get("href") for element in rule if element.tag == "constrainedElement"]
        if len(type_filters) != 1 or len(scope) != 1 or not scope[0].startswith(PROFILE_ARCHIVE + "#"):
            raise ValueError(f"Unexpected stereotype filter for {name}")
        type_calls = [call for call in expression.iter() if type_filters[0] in list(call)]
        if len(type_calls) != 1 or type_calls[0].get("includeSubtypes") != "false":
            raise ValueError(f"Unexpected subtype matching for {name}")
        scope_id = scope[0].split("#", 1)[1]
        target_id = type_filters[0].get("stereotypeId")
        source_stereotype, target_stereotype = ids[scope_id], ids[target_id]
        if source_stereotype.get(XMI + "type") != "uml:Stereotype" or target_stereotype.get(XMI + "type") != "uml:Stereotype":
            raise ValueError(f"Not a stereotype at {name}")
        if source_stereotype.get("name") + " Refined" != name or target_stereotype.get("name") != name[:3] + "Specification":
            raise ValueError(f"Unexpected rule signature for {name}")
        scope_name, target_name = source_stereotype.get("name"), target_stereotype.get("name")
        subjects = [element.get("base_Class") for element in root if local(element) == scope_name and element.get("base_Class")]
        targets = {element.get("base_Class") for element in root if local(element) == target_name and element.get("base_Class")}
        results = []
        for subject in subjects:
            matching = [(ident, supplier) for ident, client, supplier in refines if client == subject and supplier in targets]
            reverse = [(ident, client) for ident, client, supplier in refines if supplier == subject and client in targets]
            results.append({
                "subject": paths[subject],
                "subjectId": subject,
                "matchingOutgoingRefines": len(matching),
                "matchingReverseRefines": len(reverse),
                "passesIfClientIsSource": bool(matching),
                "targetIds": sorted({target for _, target in matching}),
                "reverseTargetIds": sorted({target for _, target in reverse}),
                "reverseRefineIds": sorted(ident for ident, _ in reverse),
            })
        cameovalidation = [app for app in root if local(app) == "validationRule" and app.get("base_Constraint") == rule.get(XMI + "id")]
        if len(cameovalidation) != 1:
            raise ValueError(f"Missing Cameo validation rule settings for {name}")
        report.append({
            "rule": name,
            "ruleId": rule.get(XMI + "id"),
            "cameoSeverity": cameovalidation[0].get("severity"),
            "cameoRuleExecution": "not run",
            "endpointInterpretation": "UML Abstraction client is source, supplier is target",
            "subjects": results,
        })
        lines.extend([
            f"    constraint def '{name}' {{",
            "        @CSRMv1Metadata::ValidationRuleSource {",
            f"            sourceRef = {json.dumps(MAIN_ARCHIVE + '#' + rule.get(XMI + 'id'))};",
            f"            scopeRef = {json.dumps(scope[0])};",
            f"            targetRef = {json.dumps(PROFILE_ARCHIVE + '#' + target_id)};",
            '            relation = "SysML v1 Refine: client to supplier, exact target stereotype";',
            "        }",
            "        in ref matchingRefineTargets [0..*];",
            "        SequenceFunctions::size(matchingRefineTargets) > 0",
            "    }",
        ])
    satisfy_fragment = output / "native-satisfy.fragment"
    if not satisfy_fragment.exists():
        raise ValueError("Run convert_native_satisfy.py before converting Refined rules")
    lines.extend(satisfy_fragment.read_text().rstrip().splitlines())
    lines.append("}")
    (output / "measure-validation.sysml").write_text("\n".join(lines) + "\n")
    (output / "refine-source-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {len(report)} Refined predicates plus native Satisfy rules and audited {sum(len(r['subjects']) for r in report)} source classes")


if __name__ == "__main__":
    main()
