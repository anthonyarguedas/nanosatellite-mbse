#!/usr/bin/env python3
"""Reverse fourteen Refine links and convert all 2025 technical measure classes.

Usage: python3 convert_corrected_refines.py DISTROTEMP

Writes a Data package fragment and an audit. Run convert_unit_imports.py after
this script to include the fragment in model.sysml. Other Refine links stay as-is.
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
SOURCE = "CSRM - 2025-11-18.mdzip"
PROFILE = "CSRM-Profile2.mdzip"


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def read_root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def quote(name):
    if "'" in name or "\n" in name or "\r" in name:
        raise ValueError(f"Unrepresentable identifier: {name!r}")
    return "'" + name + "'"


def qualified(path):
    return "Data::" + "::".join(quote(name) for name in path[1:])


def document(body):
    if "*/" in body:
        raise ValueError("Source text needs a SysML comment escaping decision")
    return body


def branch():
    return {"packages": OrderedDict(), "lines": []}


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source_dir = Path(sys.argv[1])
    dest = Path(__file__).resolve().parent
    audits = json.loads((dest / "refine-source-audit.json").read_text())
    satisfy_audits = json.loads((dest / "satisfy-source-audit.json").read_text())
    satisfy_by_prefix = {audit["prefix"]: audit for audit in satisfy_audits}
    if set(satisfy_by_prefix) != {"kpp", "moe", "mop", "tpm"} or len(satisfy_audits) != 4:
        raise ValueError("Expected four distinct Satisfy rule audits")
    if any(audit["propertyCount"] or len(audit["requirements"]) != 2 or
           any(subject["matchingSatisfyRelations"] for subject in audit["requirements"])
           for audit in satisfy_audits):
        raise ValueError("Satisfy property targets need explicit feature conversion")
    satisfy_subjects = {prefix: {s["requirementId"] for s in audit["requirements"]}
                        for prefix, audit in satisfy_by_prefix.items()}
    root = read_root(source_dir / SOURCE, "com.nomagic.magicdraw.uml_model.model")
    profile = read_root(source_dir / PROFILE, "com.nomagic.magicdraw.uml_model.shared_model")
    ids = {element.get(XMI + "id"): element for element in root.iter() if element.get(XMI + "id")}
    profile_ids = {element.get(XMI + "id"): element for element in profile.iter() if element.get(XMI + "id")}
    parent = {child: owner for owner in root.iter() for child in owner}
    paths = {}

    def walk(element, path):
        path = path + ((element.get("name"),) if element.get("name") else ())
        if element.get(XMI + "id"):
            paths[element.get(XMI + "id")] = path
        for child in element:
            walk(child, path)

    walk(root, ())
    abstractions = {element.get(XMI + "id"): element for element in root.iter() if element.get(XMI + "type") == "uml:Abstraction"}
    refine_ids = {element.get("base_Abstraction") for element in root if local(element) == "Refine"}
    tree = branch()

    def add(path, content):
        if path[0] != "Data":
            raise ValueError(f"Unexpected owner path: {path}")
        node = tree
        for name in path[1:]:
            node = node["packages"].setdefault(name, branch())
        node["lines"].extend(content)

    def source_metadata(ident, stereo_ref, summary, source_id):
        return [
            "@CSRMv1Metadata::ConvertedClassSource {",
            f"    sourceRef = {json.dumps(SOURCE + '#' + ident)};",
            f"    stereotypeRef = {json.dumps(stereo_ref)};",
            f"    sourceSummary = {json.dumps(summary)};",
            f"    sourceId = {json.dumps(source_id)};",
            "}",
        ]

    corrections = []
    seen_classes = set()
    for audit in audits:
        name = audit["rule"]
        prefix = name[:3]
        rule = ids[audit["ruleId"]]
        refs = [child.get("href") for child in rule if child.tag == "constrainedElement"]
        if len(refs) != 1 or not refs[0].startswith(PROFILE + "#"):
            raise ValueError(f"Unexpected constraint scope for {name}")
        scope_id = refs[0].split("#", 1)[1]
        if profile_ids[scope_id].get("name") != prefix + "Requirement":
            raise ValueError(f"Unexpected requirement stereotype for {name}")
        target_stereos = [element for element in profile_ids.values() if element.get("name") == prefix + "Specification" and element.get(XMI + "type") == "uml:Stereotype"]
        if len(target_stereos) != 1:
            raise ValueError(f"Unexpected specification stereotype for {name}")
        target_id = target_stereos[0].get(XMI + "id")
        for subject in audit["subjects"]:
            req_id = subject["subjectId"]
            reverse = subject["reverseTargetIds"]
            if subject["matchingOutgoingRefines"] != 0 or len(reverse) != 1:
                raise ValueError(f"Refine direction changed for {subject['subject']}")
            spec_id = reverse[0]
            requirement, specification = ids[req_id], ids[spec_id]
            if requirement.get(XMI + "type") != "uml:Class" or specification.get(XMI + "type") != "uml:Class":
                raise ValueError("Expected UML classes")
            req_apps = [element for element in root if element.get("base_Class") == req_id and local(element) == prefix + "Requirement"]
            spec_apps = [element for element in root if element.get("base_Class") == spec_id and local(element) == prefix + "Specification"]
            if len(req_apps) != 1 or len(spec_apps) != 1:
                raise ValueError("Missing source stereotype application")
            req_app, spec_app = req_apps[0], spec_apps[0]
            if any(child.get(XMI + "type") for child in requirement) or any(child.get(XMI + "type") not in ("uml:Comment", None) for child in specification):
                raise ValueError("Additional class content needs translation")
            original = []
            for ident in refine_ids:
                relation = abstractions[ident]
                clients = [child.get(XMI + "idref") for child in relation if child.tag == "client"]
                suppliers = [child.get(XMI + "idref") for child in relation if child.tag == "supplier"]
                if clients == [spec_id] and suppliers == [req_id]:
                    original.append(ident)
            if sorted(original) != subject["reverseRefineIds"]:
                raise ValueError(f"Reverse Refine links changed for {req_id}")
            if req_id not in seen_classes:
                seen_classes.add(req_id)
                req_lines = [f"requirement <{quote(req_app.get('Id'))}> {quote(requirement.get('name'))} {{"]
                if req_app.get("Text"):
                    req_lines.append(f"    doc /*{document(req_app.get('Text'))}*/")
                req_lines.extend("    " + line for line in source_metadata(req_id, PROFILE + "#" + scope_id, "", req_app.get("Id") or ""))
                source_refs = json.dumps([SOURCE + "#" + ident for ident in sorted(original)])
                req_lines.extend([
                    f"    ref refinedSpecs : {qualified(paths[spec_id])} [1] {{",
                    "        @CSRMv1Metadata::ReifiedRefineTargets {",
                    f"            sourceRefineIds = {json.dumps(source_refs)};",
                    f"            targetSourceRef = {json.dumps(SOURCE + '#' + spec_id)};",
                    "        }",
                    "    }",
                    f"    assert constraint refineValidation : CSRMMeasureValidation::{quote(name)} {{",
                    "        in ref matchingRefineTargets = refinedSpecs;",
                    "    }",
                ])
                if req_id not in satisfy_subjects[prefix]:
                    raise ValueError(f"Missing Satisfy validation subject: {req_id}")
                satisfy_audit = satisfy_by_prefix[prefix]
                native_type = satisfy_audit["typeName"]
                parameter = "matchingKppSatisfiers" if native_type == "KPP" else f"matching{native_type}Satisfiers"
                req_lines.extend([
                    "    // No matching measure property satisfies this requirement in the source.",
                    f"    assert constraint {prefix}SatisfyValidation : CSRMMeasureValidation::{quote(satisfy_audit['rule'])} {{",
                    f"        in attribute {parameter} : CSRMNativeMeasures::{native_type} [0];",
                    "    }",
                ])
                req_lines.append("}")
                add(paths[req_id][:-1], req_lines)
            if spec_id not in seen_classes:
                seen_classes.add(spec_id)
                spec_lines = [f"part def {quote(specification.get('name'))} {{"]
                for child in specification:
                    if child.get(XMI + "type") == "uml:Comment" and child.get("body"):
                        spec_lines.append(f"    comment /*{document(child.get('body'))}*/")
                spec_lines.extend("    " + line for line in source_metadata(spec_id, PROFILE + "#" + target_id, spec_app.get("summary") or "", spec_app.get("Id") or ""))
                spec_lines.append("}")
                add(paths[spec_id][:-1], spec_lines)
            for relation_id in sorted(original):
                relation = abstractions[relation_id]
                owner = parent[relation]
                while not owner.get("name"):
                    owner = parent[owner]
                link = [
                    f"dependency from {qualified(paths[req_id])} to {qualified(paths[spec_id])} {{",
                    "    @CSRMv1Metadata::CorrectedRefineSource {",
                    f"        sourceRef = {json.dumps(SOURCE + '#' + relation_id)};",
                    f"        originalClientRef = {json.dumps(SOURCE + '#' + spec_id)};",
                    f"        originalSupplierRef = {json.dumps(SOURCE + '#' + req_id)};",
                    "        isRefine = true;",
                    "    }",
                    "}",
                ]
                add(paths[owner.get(XMI + "id")], link)
                corrections.append({
                    "sourceRefineId": relation_id,
                    "originalClient": paths[spec_id],
                    "originalSupplier": paths[req_id],
                    "convertedClient": paths[req_id],
                    "convertedSupplier": paths[spec_id],
                    "sourceRule": name,
                })
    if len(corrections) != 14 or len(seen_classes) != 16 or sum(map(len, satisfy_subjects.values())) != 8:
        raise ValueError("Expected fourteen corrected links, sixteen source classes, and eight Satisfy subjects")

    # The third kppSpecification class has no Refine link. Keep its source
    # spelling and namespace without inventing a link or a target feature.
    technical = next(e for e in root.iter() if e.get("name") == "2 - Technical Measures" and
                     e.get(XMI + "type") == "uml:Package" and paths[e.get(XMI + "id")] ==
                     ("Data", "2 - Technical Measures"))
    remaining = [e for e in technical.iter() if e.get(XMI + "type") == "uml:Class" and
                 e.get(XMI + "id") not in seen_classes]
    if len(remaining) != 1 or len(seen_classes) + len(remaining) != 17:
        raise ValueError("New technical measure classes need translation")
    standalone = remaining[0]
    standalone_id = standalone.get(XMI + "id")
    if (standalone.get("name") != "KppB Spedification" or paths[standalone_id][:-1] != (
            "Data", "2 - Technical Measures",
            "2.1 - Technical Measures - Specifications and Requirements - Population", "2.1.4 KPP") or
            len(standalone) != 0):
        raise ValueError("Unlinked KPP specification needs separate translation")
    apps = [a for a in root if local(a) == "kppSpecification" and
            a.get("base_Class") == standalone_id]
    stereo = [e for e in profile_ids.values() if e.get("name") == "kppSpecification" and
              e.get(XMI + "type") == "uml:Stereotype"]
    if len(apps) != 1 or len(stereo) != 1 or len([a for a in root if a.get("base_Class") == standalone_id]) != 1:
        raise ValueError("Unexpected standalone KPP source stereotype")
    if any(standalone_id in [end.get(XMI + "idref") for end in rel if local(end) in ("client", "supplier")]
           for rel in root.iter() if rel.get(XMI + "type") in ("uml:Abstraction", "uml:Dependency")):
        raise ValueError("Standalone specification gained a relationship to translate")
    add(paths[standalone_id][:-1], [
        f"part def {quote(standalone.get('name'))} {{",
        *("    " + line for line in source_metadata(standalone_id, PROFILE + "#" + stereo[0].get(XMI + "id"),
                                                   apps[0].get("summary") or "", apps[0].get("Id") or "")),
        "}",
    ])
    seen_classes.add(standalone_id)
    lines = ["    // All seventeen technical measure classes and fourteen corrected Refine links."]

    def emit(node, level):
        indent = "    " * level
        for name, child in node["packages"].items():
            lines.append(f"{indent}package {quote(name)} {{")
            emit(child, level + 1)
            lines.append(f"{indent}}}")
        for element in node["lines"]:
            lines.extend(indent + line for line in element.splitlines())

    emit(tree, 1)
    (dest / "technical-measures.fragment").write_text("\n".join(lines) + "\n")
    (dest / "refine-corrections.json").write_text(json.dumps(corrections, indent=2) + "\n")
    print(f"Prepared {len(seen_classes)} elements and {len(corrections)} reversed Refine dependencies")


if __name__ == "__main__":
    main()
