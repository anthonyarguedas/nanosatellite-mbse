"""Source detail evidence and honest abstract completeness for final OATD records."""
from __future__ import annotations

import hashlib
from typing import Any, Mapping

DETAIL_FIELDS = {
    "degree": ("Degree",),
    "degree_level": ("Degree Level",),
    "publication_type": ("Publication Type", "Document Type", "Type"),
    "discipline": ("Discipline/Department", "Department/Discipline"),
    "language": ("Language",),
    "issued_date": ("Issued Date",),
}

DETAIL_SCRIPT = r"""labels => {
  const normalize = value => String(value || '').replace(/[\s\u2009\u202f]+/g, ' ').trim();
  const tables = Array.from(document.querySelectorAll('table.recordTable'));
  if (tables.length !== 1) throw new Error('Expected one Record Details table');
  const rows = Array.from(tables[0].rows);
  const read = names => {
    const matches = rows.filter(row => row.cells.length === 2 && names.includes(normalize(row.cells[0].textContent)));
    return matches.map(row => ({label: normalize(row.cells[0].textContent),
      value: normalize(row.cells[1].innerText || row.cells[1].textContent)}));
  };
  return {
    fields: Object.fromEntries(Object.entries(labels).map(([key, names]) => [key, read(names)])),
    abstract: read(['Abstract'])
  };
}"""


def abstract_state(text: str) -> str:
    if not text:
        return "absent_in_oatd"
    if text.rstrip().endswith(("…", "...")):
        return "truncated_in_oatd"
    return "complete_as_displayed_in_oatd"


async def capture(page: Any, record: dict[str, Any]) -> dict[str, Any]:
    evidence = await page.evaluate(DETAIL_SCRIPT, {k: list(v) for k, v in DETAIL_FIELDS.items()})
    abstract_rows = evidence.pop("abstract")
    if len(abstract_rows) > 1:
        raise RuntimeError("The OATD abstract field is ambiguous")
    # Preserve the entire rendered cell, including text outside child elements.
    # innerText supplies paragraph boundaries that textContent can concatenate.
    text = abstract_rows[0]["value"] if abstract_rows else ""
    record["abstract"] = text
    record["abstract_not_available"] = not bool(text)
    evidence["abstract_state"] = abstract_state(text)
    evidence["abstract_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    evidence["publication_type_basis"] = "OATD ETD index scope, with native degree and degree level retained separately"
    return validate(evidence, text)


def validate(evidence: Any, abstract: str) -> dict[str, Any]:
    if not isinstance(evidence, dict) or set(evidence) != {
        "fields", "abstract_state", "abstract_sha256", "publication_type_basis"
    }:
        raise RuntimeError("OATD detail evidence is missing")
    fields = evidence["fields"]
    if not isinstance(fields, dict) or set(fields) != set(DETAIL_FIELDS):
        raise RuntimeError("OATD detail evidence lacks its native field states")
    for key, values in fields.items():
        if not isinstance(values, list) or len(values) > 1 or any(
            not isinstance(value, dict) or set(value) != {"label", "value"}
            or value["label"] not in DETAIL_FIELDS[key]
            or not isinstance(value["value"], str) or len(value["value"]) > 100000
            for value in values
        ):
            raise RuntimeError("OATD native detail field is invalid")
    if evidence["abstract_state"] != abstract_state(abstract) or evidence["abstract_sha256"] != hashlib.sha256(abstract.encode("utf-8")).hexdigest():
        raise RuntimeError("OATD abstract completeness evidence does not match its text")
    return evidence
