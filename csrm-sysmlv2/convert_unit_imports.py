#!/usr/bin/env python3
"""Convert the CSRM basic unit imports and their ISO-80000 ValueTypes.

Usage: python3 convert_unit_imports.py DISTROTEMP MODELLIBRARIES

Deliberately narrow. Fail rather than silently map an unrecognized model element.
Quantities and units remain source XMI references in SysML v2 metadata.
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XMI = "{http://www.omg.org/spec/XMI/20131001}"
MODEL_ENTRY = "com.nomagic.magicdraw.uml_model.model"
SHARED_ENTRY = "com.nomagic.magicdraw.uml_model.shared_model"
ARCHIVES = ("ISO-80000.mdzip", "ISO-80000-Extension.mdzip")
DEPENDENCY_TARGETS = {
    "CSRM Reference Information2.mdzip#_19_0_3_2b0010b_1613258543334_43499_42727": ("CSRMExternalProjects", "CSRM Reference Information2", "CubeSat Reference Information"),
    "CSRM Reference Information2.mdzip#_19_0_3_2b0010b_1613258521460_451037_13805": ("CSRMExternalProjects", "CSRM Reference Information2", "Unit Imports"),
    "CSRM-Profile2.mdzip#_0": ("CSRMExternalProjects", "CSRM-Profile2", "CSRM Profile"),
    "CSRM Profile.mdzip#_19_0_3_2b0010b_1614441650535_642789_2693": ("CSRMExternalProjects", "CSRM Profile", "Derived Properties"),
}


def archive_root(path, entry):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read(entry))


def named_child(parent, name):
    matches = [child for child in parent if child.get("name") == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one child {name!r}, found {len(matches)}")
    return matches[0]


def quoted(name):
    if "'" in name or "\n" in name or "\r" in name:
        raise ValueError(f"Identifier needs an explicit escaping decision: {name!r}")
    return f"'{name}'"


def reference_path(path):
    return "::".join(quoted(name) for name in path)


def index_library(root):
    ids = {}
    paths = {}

    def visit(element, parents):
        path = parents + ((element.get("name"),) if element.get("name") else ())
        ident = element.get(XMI + "id")
        if ident:
            ids[ident] = element
            paths[ident] = path
        for child in element:
            visit(child, path)

    visit(root, ())
    applied = {element.get("base_DataType"): element for element in root if element.get("base_DataType")}
    return ids, paths, applied


def source_element(ref, libraries):
    archive, ident = ref.split("#", 1)
    if archive not in libraries:
        raise ValueError(f"Unsupported archive: {archive}")
    ids, paths, applications = libraries[archive]
    element = ids[ident]
    stereotype = applications.get(ident)
    if element.get(XMI + "type") != "uml:DataType" or stereotype is None or stereotype.tag.rsplit("}", 1)[-1] != "ValueType":
        raise ValueError(f"Expected a SysML v1 ValueType at {ref}")
    if set(stereotype.attrib) - {XMI + "id", "base_DataType", "quantityKind", "unit"}:
        raise ValueError(f"Additional stereotype attributes at {ref}")
    if any(child.tag != "generalization" for child in element):
        raise ValueError(f"Additional ValueType elements at {ref}")
    if not paths[ident] or paths[ident][0] != archive.removesuffix(".mdzip"):
        raise ValueError(f"Unexpected namespace at {ref}: {paths[ident]}")
    return element, stereotype, paths[ident]


def instance_name(archive, ident, libraries):
    if not ident:
        return ""
    ids, paths, _ = libraries[archive]
    if ident not in ids or ids[ident].get(XMI + "type") != "uml:InstanceSpecification":
        raise ValueError(f"Missing quantity kind or unit instance: {archive}#{ident}")
    return "::".join(paths[ident])


def parents_of(ref, libraries):
    element, _, _ = source_element(ref, libraries)
    result = []
    for generalization in element.findall("generalization"):
        general = generalization.get("general")
        if not general:
            child = generalization.find("general")
            general = child.get("href") if child is not None else None
        if not general:
            raise ValueError(f"Generalization without target at {ref}")
        result.append(general if "#" in general else ref.split("#", 1)[0] + "#" + general)
    return result


def unit_packages(source_dir, libraries):
    root = archive_root(source_dir / "CSRM - 2025-11-18.mdzip", MODEL_ENTRY)
    model = named_child(root, "Data")
    units = named_child(model, "Unit Imports")
    basic = named_child(units, "Basic Units")
    extensions = named_child(model, "CSRM Extentions")
    legends = named_child(extensions, "Legends")
    constraints = named_child(extensions, "Model Constraints")
    measure_validation = named_child(constraints, "Measure Validation")
    structure = named_child(constraints, "Structure")
    if any(element.get(XMI + "type") != "uml:Package" for element in (extensions, legends, constraints, measure_validation, structure)):
        raise ValueError("Unexpected CSRM extension namespace")
    if any(child.get(XMI + "type") not in ("uml:Package", None) for child in basic):
        raise ValueError("Unexpected element under Basic Units")
    category_ids = {package.get(XMI + "id"): package.get("name") for package in basic}
    root_imports = []
    for child in model:
        if child.get(XMI + "type") != "uml:PackageImport":
            continue
        target = child.get("importedPackage")
        if target not in category_ids:
            raise ValueError(f"Unresolved model-level package import: {target}")
        root_imports.append(category_ids[target])
    dependencies = []
    for child in model:
        if child.get(XMI + "type") != "uml:Dependency":
            continue
        clients, suppliers = child.findall("client"), child.findall("supplier")
        if len(clients) != 1 or clients[0].get(XMI + "idref") != model.get(XMI + "id") or len(suppliers) != 1:
            raise ValueError("Unsupported model-level dependency")
        target = suppliers[0].get("href")
        if target not in DEPENDENCY_TARGETS:
            raise ValueError(f"Unknown model-level dependency: {target}")
        dependencies.append(target)
    if len(dependencies) != len(DEPENDENCY_TARGETS):
        raise ValueError("Model-level dependency count changed")
    groups = []
    for package in basic:
        if package.get(XMI + "type") != "uml:Package":
            raise ValueError("Unexpected Basic Units child")
        imports = []
        for child in package:
            if child.get(XMI + "type") != "uml:ElementImport":
                raise ValueError(f"Unexpected element under {package.get('name')}")
            target = child.find("importedElement")
            if target is None or not target.get("href"):
                raise ValueError("Import without target")
            ref = target.get("href")
            source_element(ref, libraries)
            imports.append(ref)
        groups.append((package.get("name"), imports))
    return groups, root_imports, dependencies


def generate_libraries(libraries, refs):
    # Preserve the source nesting. Generalizations are ordinary attribute
    # definition specializations. Keep each quantity kind and unit as a source
    # reference, without asserting a native SysML v2 unit interpretation.
    result = {}
    for archive in ARCHIVES:
        tree = {"packages": OrderedDict(), "elements": []}
        for ref in sorted(refs):
            if not ref.startswith(archive + "#"):
                continue
            element, stereotype, path = source_element(ref, libraries)
            parent = tree
            for name in path[:-1]:
                parent = parent["packages"].setdefault(name, {"packages": OrderedDict(), "elements": []})
            parent["elements"].append((ref, element, stereotype, path))

        lines = ["// Imported ValueTypes only. Source quantity kinds and units are metadata references."]

        def emit(branch, level):
            prefix = "    " * level
            for name, subtree in branch["packages"].items():
                lines.append(f"{prefix}package {quoted(name)} {{")
                emit(subtree, level + 1)
                lines.append(f"{prefix}}}")
            for ref, element, stereotype, path in branch["elements"]:
                supers = [reference_path(source_element(target, libraries)[2]) for target in parents_of(ref, libraries)]
                spec = " :> " + ", ".join(supers) if supers else ""
                lines.append(f"{prefix}attribute def {quoted(path[-1])}{spec} {{")
                lines.append(f"{prefix}    @CSRMv1Metadata::ValueTypeSource {{")
                for key, value in (
                    ("sourceRef", ref),
                    ("quantityKindRef", archive + "#" + stereotype.get("quantityKind") if stereotype.get("quantityKind") else ""),
                    ("quantityKindName", instance_name(archive, stereotype.get("quantityKind"), libraries)),
                    ("unitRef", archive + "#" + stereotype.get("unit") if stereotype.get("unit") else ""),
                    ("unitName", instance_name(archive, stereotype.get("unit"), libraries)),
                ):
                    lines.append(f"{prefix}        {key} = {json.dumps(value)};")
                lines.append(f"{prefix}    }}")
                lines.append(f"{prefix}}}")

        emit(tree, 0)
        result[archive] = "\n".join(lines) + "\n"
    return result


def generate_model(groups, root_imports, dependencies, libraries, technical_fragment="", architecture_fragment="", customization_fragment="", duplicate_fragment="", concern_fragment=""):
    lines = [
        "// Partial conversion. See README.md for the stop point and unconverted content.",
        "package Data {",
    ]
    for name in root_imports:
        lines.append(f"    public import Data::'Unit Imports'::'Basic Units'::{quoted(name)}::*;")
    for source_ref in dependencies:
        target = (DEPENDENCY_TARGETS[source_ref][0], *(quoted(name) for name in DEPENDENCY_TARGETS[source_ref][1:]))
        lines.append(f"    dependency from Data to {'::'.join(target)};")
    lines.extend(["    package 'Unit Imports' {", "        package 'Basic Units' {"])
    for name, refs in groups:
        lines.append(f"            package {quoted(name)} {{")
        for ref in refs:
            _, _, path = source_element(ref, libraries)
            lines.append(f"                public import {reference_path(path)};")
        lines.append("            }")
    lines.extend([
        "        }",
        "    }",
        "    package 'CSRM Extentions' {",
        "        package Customizations {",
    ])
    lines.extend(customization_fragment.rstrip().splitlines())
    lines.extend([
        "        }",
        "        package Legends; // Presentation content is deferred with diagrams.",
        "        package 'Model Constraints' {",
        "            package 'Measure Validation';",
        "            package Structure;",
        "        }",
        "    }",
    ])
    if technical_fragment:
        lines.extend(technical_fragment.rstrip().splitlines())
    if architecture_fragment:
        lines.extend(architecture_fragment.rstrip().splitlines())
    duplicate_lines = duplicate_fragment.rstrip().splitlines()
    if not duplicate_lines or duplicate_lines[-1] != "    }":
        raise ValueError("Duplicate fragment must end by closing Derived Properties")
    lines.extend(duplicate_lines[:-1])
    lines.extend(concern_fragment.rstrip().splitlines())
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    source_dir, library_dir = (Path(arg) for arg in sys.argv[1:])
    libraries = {archive: index_library(archive_root(library_dir / archive, SHARED_ENTRY)) for archive in ARCHIVES}
    groups, root_imports, dependencies = unit_packages(source_dir, libraries)
    imported_refs = {ref for _, items in groups for ref in items}
    all_refs = set(imported_refs)
    pending = list(imported_refs)
    while pending:
        for parent in parents_of(pending.pop(), libraries):
            if parent not in all_refs:
                source_element(parent, libraries)
                all_refs.add(parent)
                pending.append(parent)
    rendered = generate_libraries(libraries, all_refs)
    output = Path(__file__).resolve().parent
    fragment_file = output / "technical-measures.fragment"
    fragment = fragment_file.read_text() if fragment_file.exists() else ""
    architecture_file = output / "architecture-structures.fragment"
    architecture = architecture_file.read_text() if architecture_file.exists() else ""
    customizations = (output / "cameo-customizations.fragment").read_text()
    duplicates = (output / "duplicate-navigation.fragment").read_text()
    concerns = (output / "concernof-navigation.fragment").read_text()
    (output / "model.sysml").write_text(generate_model(groups, root_imports, dependencies, libraries, fragment, architecture, customizations, duplicates, concerns))
    (output / "iso80000.sysml").write_text(rendered[ARCHIVES[0]])
    (output / "iso80000-extension.sysml").write_text(rendered[ARCHIVES[1]])
    print(f"Converted {len(groups)} unit categories, {len(root_imports)} package imports, {len(dependencies)} dependencies, {sum(len(items) for _, items in groups)} element imports, {len(all_refs)} ValueTypes")


if __name__ == "__main__":
    main()
