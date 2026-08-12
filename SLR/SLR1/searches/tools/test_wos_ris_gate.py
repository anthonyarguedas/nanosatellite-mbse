#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
FIXTURE = TOOLS.parent / "fixtures" / "wos-ris-gate-synthetic.json"
sys.path.insert(0, str(TOOLS))
import wos_ris_gate as gate  # noqa: E402


def token(label: str) -> str:
    return hashlib.sha256(f"synthetic-structure::{label}".encode("utf-8")).hexdigest()


def private_directory(path: Path) -> None:
    path.mkdir(mode=0o700)
    os.chmod(path, 0o700)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


class SyntheticFixtureTests(unittest.TestCase):
    def test_fixture_is_structure_only(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["schema"], "wos-ris-gate-synthetic/v1")
        self.assertEqual(
            fixture["artifact_class"], "synthetic_non_source_structural_fixture"
        )
        self.assertFalse(fixture["contains_source_output"])
        contract = fixture["one_record_contract"]
        self.assertEqual(contract["record_count"], 1)
        self.assertEqual(contract["source_total"], 1)
        self.assertEqual(contract["rank"], 1)
        self.assertEqual(
            contract["required_native_tags"], list(gate.REQUIRED_NATIVE_TAGS)
        )
        self.assertEqual(contract["cited_reference_count"], 2)


class PrivateCase:
    def __init__(self, root: Path, name: str, include_cited_references: bool = True):
        self.directory = root / name
        private_directory(self.directory)
        self.ris = self.directory / "native.ris"
        self.normalized = self.directory / "normalized.csv"
        self.sidecar = self.directory / "sidecar.json"
        self.merged = self.directory / "merged.json"
        self.attestation = self.directory / "attestation.json"
        self.integrity = self.directory / "integrity.json"
        self.validation = self.directory / "validation.json"
        self.accession = token("AN")
        self.query = token("QUERY")
        self._write_ris(include_cited_references)
        self._write_normalized()
        self._write_merged()
        self._write_attestation()

    def _write_ris(self, include_cited_references: bool) -> None:
        lines = [
            "TY  - JOUR",
            f"AN  - {self.accession}",
            f"DO  - {token('DO')}",
            f"TI  - {token('TI')}",
            f"AU  - {token('AU')}",
            "PY  - 2026",
            f"AB  - {token('AB')}",
            f" {token('AB-CONTINUATION')}",
            f"WE  - {token('WE')}",
        ]
        if include_cited_references:
            lines.extend((f"CR  - {token('CR-ONE')}", f"CR  - {token('CR-TWO')}"))
        lines.append("ER  -")
        self.ris.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_normalized(self) -> None:
        row = {
            "Search source": gate.SOURCE_LABEL,
            "Query": self.query,
            "Rank": "1",
            "Source total": "1",
            "Paper ID": self.accession,
            "DOI": token("DO"),
            "Title": token("TI"),
            "Authors": token("AU"),
            "Publication year": "2026",
            "Abstract": token("AB"),
        }
        with self.normalized.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)

    def _write_merged(self) -> None:
        write_json(
            self.merged,
            {
                "dedup_summary": {
                    "raw_results": 1,
                    "unique_results": 1,
                    "duplicates_removed": 0,
                },
                "results": [
                    {
                        "sources": [gate.CANONICAL_SOURCE],
                        "paperId": self.accession,
                    }
                ],
            },
        )

    def _write_attestation(self) -> None:
        write_json(
            self.attestation,
            {
                "schema": "wos-ris-gate-attestation/v1",
                "query_sha256": gate.sha256_text(self.query),
                "source_total": 1,
                "controls": {key: True for key in gate.ATTESTATION_CONTROL_KEYS},
                "ordinary_export": {
                    key: key != "authentication_or_login_redirect"
                    for key in gate.ATTESTATION_EXPORT_KEYS
                },
            },
        )

    def create_sidecar(self) -> None:
        raw, records = gate.read_ris(self.ris)
        gate.write_private_json(self.sidecar, gate.sidecar_payload(raw, records, 1))


class GateEndToEndTests(unittest.TestCase):
    def invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        output = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = gate.main(arguments)
        return status, output.getvalue(), errors.getvalue()

    def test_private_sidecar_validation_and_reconciliation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pass_one = PrivateCase(root, "one")
            pass_two = PrivateCase(root, "two")

            status, stdout, stderr = self.invoke(
                [
                    "sidecar",
                    "--input",
                    str(pass_one.ris),
                    "--output-path",
                    str(pass_one.sidecar),
                ]
            )
            self.assertEqual(status, 0, stderr)
            self.assertNotIn(pass_one.accession, stdout)
            self.assertEqual(stat.S_IMODE(pass_one.sidecar.stat().st_mode), 0o600)
            sidecar = json.loads(pass_one.sidecar.read_text(encoding="utf-8"))
            self.assertNotIn(pass_one.accession, json.dumps(sidecar))
            self.assertEqual(len(sidecar["records"][0]["cited_references"]), 2)

            pass_two.create_sidecar()
            status, stdout, stderr = self.invoke(
                [
                    "integrity",
                    "--input",
                    str(pass_one.ris),
                    "--output-path",
                    str(pass_one.integrity),
                ]
            )
            self.assertEqual(status, 0, stderr)
            self.assertNotIn(pass_one.accession, stdout)
            integrity = pass_one.integrity.read_text(encoding="utf-8")
            self.assertNotIn(pass_one.accession, integrity)
            self.assertNotIn(token("TI"), integrity)

            status, stdout, stderr = self.invoke(
                [
                    "validate",
                    "--ris",
                    str(pass_one.ris),
                    "--normalized",
                    str(pass_one.normalized),
                    "--sidecar",
                    str(pass_one.sidecar),
                    "--merged",
                    str(pass_one.merged),
                    "--attestation",
                    str(pass_one.attestation),
                    "--output-path",
                    str(pass_one.validation),
                ]
            )
            self.assertEqual(status, 0, stderr)
            self.assertNotIn(pass_one.accession, stdout)
            validation = json.loads(pass_one.validation.read_text(encoding="utf-8"))
            self.assertTrue(validation["pass"])
            validation_text = json.dumps(validation)
            self.assertNotIn(pass_one.accession, validation_text)
            self.assertNotIn(token("TI"), validation_text)
            self.assertNotIn(token("CR-ONE"), validation_text)

            reconciliation = root / "two-pass.json"
            status, stdout, stderr = self.invoke(
                [
                    "reconcile",
                    "--pass-one-ris",
                    str(pass_one.ris),
                    "--pass-one-normalized",
                    str(pass_one.normalized),
                    "--pass-one-sidecar",
                    str(pass_one.sidecar),
                    "--pass-one-merged",
                    str(pass_one.merged),
                    "--pass-one-attestation",
                    str(pass_one.attestation),
                    "--pass-two-ris",
                    str(pass_two.ris),
                    "--pass-two-normalized",
                    str(pass_two.normalized),
                    "--pass-two-sidecar",
                    str(pass_two.sidecar),
                    "--pass-two-merged",
                    str(pass_two.merged),
                    "--pass-two-attestation",
                    str(pass_two.attestation),
                    "--output-path",
                    str(reconciliation),
                ]
            )
            self.assertEqual(status, 0, stderr)
            result = json.loads(reconciliation.read_text(encoding="utf-8"))
            self.assertTrue(result["pass"])
            self.assertTrue(result["reconciliation"]["opaque_native_order_stable"])
            reconciliation_text = json.dumps(result)
            self.assertNotIn(pass_one.accession, reconciliation_text)
            self.assertNotIn(token("CR-TWO"), reconciliation_text)

    def test_no_clobber_and_private_directory_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = PrivateCase(root, "private")
            status, _, stderr = self.invoke(
                [
                    "integrity",
                    "--input",
                    str(case.ris),
                    "--output-path",
                    str(case.integrity),
                ]
            )
            self.assertEqual(status, 0, stderr)
            status, _, stderr = self.invoke(
                [
                    "integrity",
                    "--input",
                    str(case.ris),
                    "--output-path",
                    str(case.integrity),
                ]
            )
            self.assertEqual(status, 2)
            self.assertNotIn(case.accession, stderr)

            exposed = root / "exposed"
            exposed.mkdir(mode=0o755)
            os.chmod(exposed, 0o755)
            with self.assertRaises(gate.GateError):
                gate.write_private_json(exposed / "blocked.json", {"safe": True})

    def test_missing_cited_references_fails_closed_without_content_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = PrivateCase(root, "missing-cr", include_cited_references=False)
            case.create_sidecar()
            payload = gate.validation_payload(
                case.ris,
                case.normalized,
                case.sidecar,
                case.merged,
                case.attestation,
            )
            self.assertFalse(payload["pass"])
            self.assertEqual(payload["sidecar"]["cited_reference_count"], 0)
            self.assertNotIn(case.accession, json.dumps(payload))

    def test_cited_reference_hash_is_bound_to_native(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = PrivateCase(root, "tampered-sidecar")
            case.create_sidecar()
            sidecar = json.loads(case.sidecar.read_text(encoding="utf-8"))
            sidecar["records"][0]["cited_references"] = [token("TAMPERED")]
            write_json(case.sidecar, sidecar)
            payload = gate.validation_payload(
                case.ris,
                case.normalized,
                case.sidecar,
                case.merged,
                case.attestation,
            )
            self.assertFalse(payload["pass"])
            self.assertFalse(payload["sidecar"]["cited_references_match_native"])
            self.assertNotIn(token("TAMPERED"), json.dumps(payload))

    def test_attestation_rejects_extra_source_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = PrivateCase(root, "unsafe-attestation")
            attestation = json.loads(case.attestation.read_text(encoding="utf-8"))
            attestation["url"] = "context-not-allowed"
            write_json(case.attestation, attestation)
            with self.assertRaises(gate.GateError):
                gate.load_attestation(case.attestation)


class OfflineImplementationTests(unittest.TestCase):
    def test_tool_has_no_browser_or_network_dependency_or_static_route(self) -> None:
        source = (TOOLS / "wos_ris_gate.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        forbidden = {"requests", "httpx", "selenium", "playwright", "urllib", "socket"}
        self.assertFalse(imports & forbidden)
        self.assertNotRegex(source, r"https?://")
        self.assertNotIn("/" + "Users/", source)
        self.assertNotIn("/" + "var" + "/folders/", source)
        self.assertNotIn("CDP", source)
        self.assertNotIn("_".join(("browser", "harness")), source)
        self.assertNotIn("document.querySelector", source)


if __name__ == "__main__":
    unittest.main()
