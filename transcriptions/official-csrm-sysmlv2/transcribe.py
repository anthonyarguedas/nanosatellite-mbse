#!/usr/bin/env python3
"""Reproducible SysML v2 lowering of the official CSRM vendor-neutral XMI.

This is a semantic transcription, not a UML/SysML v1 profile interpreter.
The original XMI is retained for fields that have no exact SysML v2 equivalent.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
from xml.etree import ElementTree as ET

XMI = "{http://www.omg.org/spec/XMI/20131001}"
DECLARATIONS = {
    "uml:Model", "uml:Package", "uml:Class", "uml:Actor", "uml:Activity", "uml:UseCase"
}
RELATIONSHIPS = {"uml:Association", "uml:Abstraction", "uml:Dependency"}
NODE_TYPES = {
    "uml:ActivityParameterNode", "uml:CallBehaviorAction", "uml:InitialNode",
    "uml:ActivityFinalNode", "uml:FlowFinalNode", "uml:ForkNode", "uml:JoinNode",
    "uml:AcceptEventAction",
}
DOCUMENTED_ONLY = {
    "uml:Comment", "uml:Generalization", "uml:ActivityPartition", "uml:Trigger",
    "uml:TimeEvent", "uml:TimeExpression", "uml:LiteralString",
    "uml:LiteralUnlimitedNatural", "uml:ProfileApplication",
}


class PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"head", "style", "script"}:
            self.skip += 1
        if tag in {"p", "br", "li", "div", "tr"} and not self.skip:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"head", "style", "script"}:
            self.skip -= 1


def text(value: str) -> str:
    if "<html" in value.lower() or "<br" in value.lower():
        parser = PlainText()
        parser.feed(value)
        value = "".join(parser.parts)
    return "\n".join(line.strip() for line in unescape(value).splitlines() if line.strip())


def quote(name: str) -> str:
    if "'" in name or "\\" in name or "\n" in name:
        raise ValueError(f"Unsupported XMI identifier: {name!r}")
    return "'" + name + "'"


def kind(element: ET.Element) -> str | None:
    return element.get(XMI + "type")


def identifier(element: ET.Element) -> str | None:
    return element.get(XMI + "id")


def child_ref(element: ET.Element, label: str) -> str | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == label:
            return child.get(XMI + "idref") or child.get("href")
    return None


def attrs(element: ET.Element) -> dict[str, str]:
    return {key.rsplit("}", 1)[-1]: value for key, value in element.attrib.items()}


class Transcriber:
    def __init__(self, source: Path) -> None:
        self.source = source
        profile_map = Path(__file__).resolve().parent / "profile-map.json"
        self.profile_stereotypes = json.loads(profile_map.read_text(encoding="utf-8"))["stereotypes"]
        self.original = source.read_bytes()
        root = ET.fromstring(self.original)
        self.model = next(e for e in root if kind(e) == "uml:Model")
        self.id_to_element = {identifier(e): e for e in self.model.iter() if identifier(e)}
        self.parents = {id(child): parent for parent in self.model.iter() for child in parent}
        self.stereotypes: dict[str, list[dict[str, object]]] = defaultdict(list)
        for element in root:
            if element is self.model:
                continue
            for key, value in element.attrib.items():
                if key.startswith("base_"):
                    self.stereotypes[value].append({
                        "name": element.tag.rsplit("}", 1)[-1],
                        "uri": element.tag.split("}", 1)[0].removeprefix("{") if "}" in element.tag else "",
                        "attributes": attrs(element),
                    })
        self.comments: dict[str, list[ET.Element]] = defaultdict(list)
        self.comment_targets: dict[str, list[str]] = {}
        for element in self.model.iter():
            if kind(element) != "uml:Comment":
                continue
            targets = [c.get(XMI + "idref") for c in element if c.tag.endswith("annotatedElement")]
            targets = [target for target in targets if target in self.id_to_element]
            if not targets:
                parent = self.parents.get(id(element))
                if parent is not None and identifier(parent):
                    targets = [identifier(parent)]
            self.comment_targets[identifier(element)] = targets
            for target in targets:
                self.comments[target].append(element)
        self.names: dict[str, str] = {}
        self.paths: dict[str, str] = {}
        self.record: dict[str, dict[str, object]] = {}
        self.lines: list[str] = []
        self.used: set[str] = set()
        self._index_names(self.model, "OfficialCSRM")

    def _index_names(self, element: ET.Element, parent_path: str) -> None:
        ty = kind(element)
        id_ = identifier(element)
        if ty in DECLARATIONS:
            name = element.get("name") or f"unnamed_{id_[-8:]}"
            path = parent_path + "::" + quote(name)
            self.names[id_] = name
            self.paths[id_] = path
        else:
            path = parent_path
        for index, child in enumerate(element):
            child_ty = kind(child)
            child_id = identifier(child)
            if child_ty in DECLARATIONS:
                self._index_names(child, path)
            elif child_ty == "uml:Property" and child.tag.endswith("ownedAttribute"):
                name = child.get("name") or f"property_{index}"
                self.names[child_id] = name
                self.paths[child_id] = path + "::" + quote(name)
            elif child_ty == "uml:Operation":
                name = child.get("name") or f"operation_{index}"
                self.names[child_id] = name
                self.paths[child_id] = path + "::" + quote(name)
                for param_index, param in enumerate(child):
                    if kind(param) == "uml:Parameter":
                        self.names[identifier(param)] = f"parameter_{param_index}"
                        self.paths[identifier(param)] = self.paths[child_id] + f"::parameter_{param_index}"
            elif child_ty in NODE_TYPES:
                name = f"node_{index}"
                self.names[child_id] = name
                self.paths[child_id] = path + "::" + quote(name)
                for pin_index, pin in enumerate(child):
                    if kind(pin) in ("uml:InputPin", "uml:OutputPin"):
                        self.names[identifier(pin)] = f"pin_{pin_index}"
                        self.paths[identifier(pin)] = self.paths[child_id] + f"::pin_{pin_index}"
            elif child_ty == "uml:Parameter":
                self.names[child_id] = f"parameter_{index}"
                self.paths[child_id] = path + f"::parameter_{index}"

    def emit(self, depth: int, line: str) -> None:
        self.lines.append("    " * depth + line)

    def note(self, element: ET.Element, depth: int, extra: list[str] | None = None) -> None:
        id_ = identifier(element)
        for stereotype in self.stereotypes.get(id_, []):
            if stereotype["uri"].startswith("https://www.omg.org/spec/CSRM/"):
                self.emit(depth, "@" + self.profile_stereotypes[stereotype["name"]]["sysml"] + ";")
        data = [f"Source XMI: {id_}"]
        for stereotype in self.stereotypes.get(id_, []):
            properties = stereotype["attributes"]
            fields = ", ".join(f"{key}={value}" for key, value in properties.items()
                               if key != "id" and not key.startswith("base_"))
            data.append(f"Stereotype {stereotype['name']}" + (f": {fields}" if fields else ""))
        for comment in self.comments.get(id_, []):
            c_stereos = ", ".join(s["name"] for s in self.stereotypes.get(identifier(comment), []))
            data.append(f"Comment {identifier(comment)}" + (f" ({c_stereos})" if c_stereos else ""))
            data.append(text(comment.get("body", "")))
            self.used.add(identifier(comment))
        data.extend(extra or [])
        # Include source-only timing, partition, and profile records at their owner.
        def source_only_descendants(owner: ET.Element):
            for child in owner:
                ty = kind(child)
                if ty in DOCUMENTED_ONLY and ty not in {"uml:Comment", "uml:Generalization"}:
                    yield child
                    yield from source_only_descendants(child)
                elif ty is None:
                    yield from source_only_descendants(child)
        for child in source_only_descendants(element):
            data.append(f"Source-only {kind(child)} {identifier(child)}: " + json.dumps(attrs(child), ensure_ascii=False))
        # For requirements only the stereotype Text is the normative requirement
        # documentation. Provenance and advice stay as SysML comments.
        requirement = next((s for s in self.stereotypes.get(id_, []) if s["name"].endswith("Requirement")), None)
        if requirement and requirement["attributes"].get("Text", "").strip():
            statement = text(requirement["attributes"]["Text"]).replace("*/", "* /")
            self.emit(depth, "doc /* " + statement + " */")
        body = "\n".join(part for part in data if part).replace("*/", "* /")
        annotation = "comment" if requirement else "doc"
        self.emit(depth, annotation + " /* " + body.replace("\n", "\n" + "    " * depth) + " */")
        if id_:
            self.used.add(id_)

    def ledger(self, element: ET.Element, mapping: str, reason: str = "") -> None:
        id_ = identifier(element)
        if id_:
            self.record[id_] = {
                "source_kind": kind(element),
                "source_name": element.get("name"),
                "target": mapping,
                "attributes": attrs(element),
                "stereotypes": self.stereotypes.get(id_, []),
                "note": reason,
            }
            self.used.add(id_)

    def ref(self, id_: str | None) -> str | None:
        return self.paths.get(id_)

    def property(self, element: ET.Element, depth: int) -> None:
        id_ = identifier(element)
        name = self.names[id_]
        target = self.ref(element.get("type"))
        attr_type = child_ref(element, "type")
        aggregate = element.get("aggregation") == "composite"
        prefix = "part" if aggregate else "ref part"
        if target:
            declaration = f"{prefix} {quote(name)} : {target}"
        else:
            declaration = f"attribute {quote(name)}"
        upper = next((c.get("value") for c in element if c.tag.endswith("upperValue")), None)
        if upper == "*":
            declaration += " [1..*]"
        self.emit(depth, declaration + " {")
        self.note(element, depth + 1, [
            f"UML aggregation: {element.get('aggregation', 'none')}",
            f"UML association: {element.get('association', 'none')}",
            f"External type: {attr_type}" if attr_type else "",
        ])
        self.emit(depth, "}")
        self.ledger(element, self.paths[id_])
        for child in element:
            if kind(child):
                self.document_helper(child, self.paths[id_])

    def association(self, element: ET.Element, depth: int, index: int, parent_path: str) -> None:
        id_ = identifier(element)
        name = f"association_{index}"
        path = parent_path + "::" + name
        self.emit(depth, f"connection def {name} {{")
        ends = [self.id_to_element[c.get(XMI + "idref")] for c in element
                if c.tag.endswith("memberEnd") and c.get(XMI + "idref") in self.id_to_element]
        if len(ends) != 2:
            raise ValueError(f"Association {id_} has {len(ends)} ends")
        self.note(element, depth + 1, ["UML end details are in the source map (SysML v2 connector ends have fixed [1..1] multiplicity)."])
        for number, end in enumerate(ends, 1):
            ref = self.ref(end.get("type"))
            if not ref:
                raise ValueError(f"Association {id_} has untyped end {identifier(end)}")
            self.emit(depth + 1, f"end end{number} : {ref} {{")
            self.note(end, depth + 2, [f"UML end name: {end.get('name', '(unnamed)')}"])
            self.emit(depth + 1, "}")
            self.ledger(end, path + f"::end{number}")
        self.emit(depth, "}")
        self.ledger(element, path)

    def dependency(self, element: ET.Element, depth: int, index: int, parent_path: str) -> None:
        source = self.ref(child_ref(element, "client"))
        target = self.ref(child_ref(element, "supplier"))
        if not source or not target:
            raise ValueError(f"Unresolved dependency {identifier(element)}: {source} -> {target}")
        name = f"relationship_{index}"
        self.emit(depth, f"dependency {name} from {source} to {target} {{")
        self.note(element, depth + 1, ["UML kind: " + kind(element)])
        self.emit(depth, "}")
        self.ledger(element, parent_path + "::" + name)

    def parameter(self, element: ET.Element, depth: int, target_path: str) -> None:
        id_ = identifier(element)
        name = self.names[id_]
        direction = element.get("direction", "in")
        qualifier = {"return": "out", "in": "in", "out": "out", "inout": "inout"}.get(direction, "in")
        self.emit(depth, f"{qualifier} item {name} {{")
        self.note(element, depth + 1, [
            f"UML parameter name: {element.get('name', '(unnamed)')}",
            f"UML direction: {direction}",
            f"UML type: {element.get('type') or child_ref(element, 'type') or '(none)'}",
        ])
        self.emit(depth, "}")
        self.ledger(element, target_path + "::" + name)

    def node(self, element: ET.Element, depth: int) -> None:
        id_ = identifier(element)
        name = self.names[id_]
        # A UML CallBehaviorAction owns input/output pins that need not conform
        # to the SysML v2 definition's parameter directions. Preserve its call
        # target as a dependency instead of claiming a conforming typed usage.
        self.emit(depth, f"action {name} {{")
        self.note(element, depth + 1, [
            f"UML node kind: {kind(element)}",
            f"UML node name: {element.get('name', '(unnamed)')}",
            f"UML behavior: {element.get('behavior', '(none)')}",
            f"UML parameter: {element.get('parameter', '(none)')}",
        ])
        for pin in element:
            if kind(pin) in ("uml:InputPin", "uml:OutputPin"):
                pin_id = identifier(pin)
                qualifier = "in" if kind(pin) == "uml:InputPin" else "out"
                self.emit(depth + 1, f"{qualifier} item {self.names[pin_id]} {{")
                self.note(pin, depth + 2, [
                    f"UML pin name: {pin.get('name', '(unnamed)')}",
                    f"UML type: {pin.get('type') or child_ref(pin, 'type') or '(none)'}",
                ])
                self.emit(depth + 1, "}")
                self.ledger(pin, self.paths[pin_id])
                for child in pin:
                    if kind(child):
                        self.document_helper(child, self.paths[pin_id])
        self.emit(depth, "}")
        self.ledger(element, self.paths[id_])
        for child in element:
            if kind(child) and kind(child) not in ("uml:InputPin", "uml:OutputPin"):
                self.document_helper(child, self.paths[id_])

    def activity(self, element: ET.Element, depth: int, path: str) -> None:
        for child in element:
            ty = kind(child)
            if ty == "uml:Parameter":
                self.parameter(child, depth, path)
            elif ty in NODE_TYPES:
                self.node(child, depth)
            elif ty in ("uml:ControlFlow", "uml:ObjectFlow"):
                # Defer until all node and pin declarations have been indexed.
                continue
            elif ty == "uml:ActivityPartition":
                self.document_helper(child, path)
        for node in (c for c in element if kind(c) == "uml:CallBehaviorAction" and self.ref(c.get("behavior"))):
            name = self.names[identifier(node)]
            self.emit(depth, f"dependency call_{name} from {name} to {self.ref(node.get('behavior'))};")
        for index, edge in enumerate((c for c in element if kind(c) in ("uml:ControlFlow", "uml:ObjectFlow")), 1):
            source = self.ref(edge.get("source"))
            target = self.ref(edge.get("target"))
            if not source or not target:
                raise ValueError(f"Unresolved activity edge {identifier(edge)}")
            # Local paths make node and pin connections explicit in the action definition.
            prefix = path + "::"
            a = source.removeprefix(prefix).replace("::pin_", ".pin_")
            b = target.removeprefix(prefix).replace("::pin_", ".pin_")
            if kind(edge) == "uml:ControlFlow":
                name = f"controlFlow_{index}"
                self.emit(depth, f"succession {name} first {a} then {b} {{")
                self.note(edge, depth + 1, ["UML ControlFlow between indexed node endpoints."])
                self.emit(depth, "}")
                self.ledger(edge, path + "::" + name, "SysML v2 succession")
            else:
                name = f"objectFlow_{index}"
                self.emit(depth, f"flow {name} from {a} to {b} {{")
                self.note(edge, depth + 1, ["UML ObjectFlow between indexed node or pin endpoints."])
                self.emit(depth, "}")
                self.ledger(edge, path + "::" + name)
            for child in edge:
                if kind(child):
                    self.document_helper(child, self.record[identifier(edge)]["target"])

    def document_helper(self, element: ET.Element, owner: str) -> None:
        # UML elements without a direct, lossless SysML v2 construct are retained
        # verbatim in source/CSRM.xmi and indexed with their owner in the source map.
        id_ = identifier(element)
        if id_:
            self.ledger(element, owner, "Source-only detail. See original XMI and owner documentation.")
        for child in element:
            if kind(child):
                self.document_helper(child, owner)

    def declaration(self, element: ET.Element, depth: int) -> None:
        ty = kind(element)
        id_ = identifier(element)
        path = self.paths[id_]
        name = quote(self.names[id_])
        stereo = {s["name"] for s in self.stereotypes.get(id_, [])}
        if ty in ("uml:Model", "uml:Package"):
            prefix = "package"
        elif ty == "uml:Class":
            prefix = "requirement def" if any(s.endswith("Requirement") for s in stereo) else "part def"
        elif ty == "uml:Actor":
            prefix = "part def"
        elif ty == "uml:Activity":
            prefix = "action def"
        else:
            prefix = "use case def"
        if element.get("isAbstract") == "true" and ty == "uml:Class":
            prefix = "abstract " + prefix
        self.emit(depth, f"{prefix} {name} {{")
        self.note(element, depth + 1, [f"UML kind: {ty}"])
        self.ledger(element, path)
        for child in element:
            if kind(child) == "uml:Generalization":
                self.emit(depth + 1, "// UML generalization " + identifier(child) + " to " + str(child_ref(child, "general")))
                self.document_helper(child, path)
        if ty == "uml:Activity":
            self.activity(element, depth + 1, path)
        for index, child in enumerate(element):
            child_ty = kind(child)
            if child_ty in DECLARATIONS:
                self.declaration(child, depth + 1)
            elif child_ty == "uml:Property" and child.tag.endswith("ownedAttribute"):
                self.property(child, depth + 1)
            elif child_ty == "uml:Operation":
                op_path = self.paths[identifier(child)]
                self.emit(depth + 1, f"action def {quote(self.names[identifier(child)])} {{")
                self.note(child, depth + 2, ["UML operation. Method reference: " + str(child_ref(child, "method"))])
                self.ledger(child, op_path)
                for param in child:
                    if kind(param) == "uml:Parameter":
                        self.parameter(param, depth + 2, op_path)
                self.emit(depth + 1, "}")
            elif child_ty == "uml:Association":
                self.association(child, depth + 1, index, path)
            elif child_ty in ("uml:Abstraction", "uml:Dependency"):
                self.dependency(child, depth + 1, index, path)
            elif child_ty in DOCUMENTED_ONLY:
                if child_ty != "uml:Generalization":
                    self.document_helper(child, path)
            elif child_ty in NODE_TYPES or child_ty in ("uml:Parameter", "uml:ControlFlow", "uml:ObjectFlow", "uml:ActivityPartition"):
                # Already emitted by activity().
                pass
            elif child_ty:
                raise ValueError(f"Unhandled direct UML child {child_ty} in {path}")
        self.emit(depth, "}")

    def generate(self) -> tuple[str, dict[str, object], dict[str, object]]:
        self.emit(0, "// INCOSE SSWG and OMG SDTF, CubeSat System Reference Model, CC BY 4.0.")
        self.emit(0, "// Direct source: ObjectManagementGroup/CSRM, Distro/CSRM XMI/CSRM.xmi.")
        self.emit(0, "// Generated by transcribe.py from the pinned vendor-neutral XMI. See README.md.")
        self.emit(0, "// Load with CSRMProfile.sysml in the same model project.")
        self.emit(0, "package OfficialCSRM {")
        self.emit(1, "doc /* SysML v2 transcription of the official CSRM XMI model. The CSRM Profile is a distinct SysML v1 specification. */")
        self.declaration(self.model, 1)
        self.emit(0, "}")
        for element in self.model.iter():
            id_ = identifier(element)
            if id_ and kind(element) and id_ not in self.used:
                raise ValueError(f"Unaccounted UML element {kind(element)} {id_}")
        counts = Counter(kind(e) for e in self.model.iter() if kind(e))
        report = {
            "source": "https://github.com/ObjectManagementGroup/CSRM/blob/69c7f021fd1b2b0e9135dc9e6f926c12e514de7e/Distro/CSRM%20XMI/CSRM.xmi",
            "sha256": hashlib.sha256(self.original).hexdigest(),
            "source_kind_counts": dict(sorted(counts.items())),
            "source_uml_elements": sum(counts.values()),
            "mapped_ids": len(self.record),
            "unaccounted_ids": [],
            "lowering": {
                "declarations": sorted(DECLARATIONS),
                "relationships": sorted(RELATIONSHIPS),
                "activity_nodes": sorted(NODE_TYPES),
                "documented_only": sorted(DOCUMENTED_ONLY),
                "activity_edges": ["uml:ControlFlow", "uml:ObjectFlow"],
                "properties": "ownedAttribute usages and association end features",
                "parameters": "untyped in/out items with original types in source map",
            },
        }
        return "\n".join(self.lines) + "\n", self.record, report


def main() -> None:
    folder = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=folder / "source" / "CSRM.xmi")
    parser.add_argument("--output-dir", type=Path, default=folder)
    args = parser.parse_args()
    model, mapping, audit = Transcriber(args.source).generate()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "CSRM.sysml").write_text(model, encoding="utf-8")
    (args.output_dir / "source-map.json").write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "coverage.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sysml": str(args.output_dir / "CSRM.sysml"), "source_uml_elements": audit["source_uml_elements"], "mapped_ids": audit["mapped_ids"]}))


if __name__ == "__main__":
    main()
