#!/usr/bin/env python3
"""Represent official CSRM v1 stereotype names as SysML v2 metadata definitions.

The profile's UML metaclass extensions and OCL constraints remain in its XMI.
They cannot be asserted to have equivalent SysML v2 semantics.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from transcribe import XMI, attrs, identifier, kind, quote, text

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "source" / "CSRM-Profile-23-11-16.xmi"


def main() -> None:
    data = SOURCE.read_bytes()
    root = ET.fromstring(data)
    top = next(element for element in root if kind(element) == "uml:Profile")
    lines = [
        "// Derived from INCOSE SSWG / OMG SDTF CSRM Profile XMI, CC BY 4.0.",
        "// Stereotype labels are metadata definitions. OCL and UML extensions remain in the XMI.",
        "package OfficialCSRMProfile {",
    ]
    records: dict[str, object] = {}
    for sub in (child for child in top if kind(child) == "uml:Profile"):
        lines.append(f"    package {quote(sub.get('name'))} {{")
        for stereotype in (child for child in sub if kind(child) == "uml:Stereotype"):
            name = stereotype.get("name")
            id_ = identifier(stereotype)
            path = "OfficialCSRMProfile::" + quote(sub.get("name")) + "::" + quote(name)
            details = []
            for child in stereotype.iter():
                if child is stereotype:
                    continue
                if kind(child) in ("uml:Property", "uml:Generalization", "uml:Constraint", "uml:OpaqueExpression"):
                    details.append({"kind": kind(child), "attributes": attrs(child),
                                    "references": [c.attrib for c in child if c.get("href") or c.get(XMI + "idref")]})
            docs = [text(c.get("body", "")) for c in stereotype if kind(c) == "uml:Comment"]
            comment = f"Source profile stereotype: {name}\nXMI id: {id_}\n" + "\n".join(docs)
            comment = comment.replace("*/", "* /")
            lines.append(f"        metadata def {quote(name)} {{")
            lines.append("            doc /* " + comment.replace("\n", "\n            ") + " */")
            if details:
                for item in details:
                    lines.append("            // Source-only " + json.dumps(item, ensure_ascii=False))
            lines.append("        }")
            records[name] = {"xmi_id": id_, "profile": sub.get("name"), "sysml": path,
                             "source_features": details}
        lines.append("    }")
    lines.append("}")
    (BASE / "CSRMProfile.sysml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (BASE / "profile-map.json").write_text(json.dumps({
        "source": "https://github.com/ObjectManagementGroup/CSRM/blob/69c7f021fd1b2b0e9135dc9e6f926c12e514de7e/Distro/CSRM%20XMI/23-11-16.xmi",
        "sha256": hashlib.sha256(data).hexdigest(), "stereotypes": records,
        "scope": "Stereotype labels only. UML profile extensions and OCL constraints retain their original XMI semantics.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Represented {len(records)} CSRM profile stereotypes as metadata definitions")


if __name__ == "__main__":
    main()
