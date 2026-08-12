#!/usr/bin/env python3
"""Offline contract tests for the version-locked IAF local matcher wrapper."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).with_name("iaf_title_abstract_matcher.py")
SEARCHES_PATH = SCRIPT_PATH.parents[1]
DICTIONARY_PATH = SEARCHES_PATH / "search-concept-dictionary.json"
MATCHER_PATH = SCRIPT_PATH.with_name("concept_matcher.py")
FIXTURE_PATH = SEARCHES_PATH / "fixtures/iaf-title-abstract-matcher-v1.6.json"
SPEC = importlib.util.spec_from_file_location("iaf_title_abstract_matcher_tested", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not import {SCRIPT_PATH}")
iaf = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = iaf
SPEC.loader.exec_module(iaf)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def adapter_record(paper_id: object, *, title: str = "CubeSat MBSE") -> dict[str, object]:
    """Return an adapter-shaped record with metadata that matching must ignore."""
    return {
        "paperId": paper_id,
        "title": title,
        "abstract": None,
        "authors": [{"name": "Synthetic Author"}],
        "eventCode": "IAC-2024",
        "openAccess_pdf": {},
        "publicationTitle": "Synthetic IAC proceedings",
    }


class AdapterEnvelopeContractTests(unittest.TestCase):
    def test_official_results_envelope_preserves_exact_paper_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "adapter.json"
            first_id = "iaf-digital-library:IAC-2024:paper-001"
            second_id = "iaf-digital-library:IAC-2024:CubeSat-MBSE"
            second = adapter_record(second_id, title="Unrelated catalogue")
            second["authors"] = [{"name": "CubeSat MBSE"}]
            write_json(
                input_path,
                {
                    "query": "synthetic",
                    "results": [adapter_record(first_id), second],
                    "output_metadata": {"status": "success"},
                },
            )
            report = iaf.match_json(DICTIONARY_PATH, MATCHER_PATH, input_path)

        self.assertEqual(report["input_mode"], "official_iaf_adapter_results_envelope")
        self.assertEqual(
            [record["record_id"] for record in report["records"]],
            [first_id, second_id],
        )
        self.assertTrue(report["records"][0]["tags"]["iaf_b_core"])
        self.assertFalse(report["records"][1]["tags"]["iaf_p_tag"])
        self.assertFalse(report["records"][1]["tags"]["iaf_m_tag"])
        self.assertNotIn("paperId", report["records"][0]["ignored_input_keys"])
        self.assertEqual(
            report["records"][0]["ignored_input_keys"],
            ["authors", "eventCode", "openAccess_pdf", "publicationTitle"],
        )

    def test_missing_or_duplicate_adapter_paper_ids_fail_closed(self) -> None:
        cases = (
            (
                "missing",
                {"results": [adapter_record(None)]},
                "non-empty stable paperId",
            ),
            (
                "blank",
                {"results": [adapter_record(" ")]},
                "non-empty stable paperId",
            ),
            (
                "duplicate",
                {
                    "results": [
                        adapter_record("iaf-digital-library:IAC-2024:duplicate"),
                        adapter_record("iaf-digital-library:IAC-2024:duplicate"),
                    ]
                },
                "duplicate stable paperId",
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            for name, document, message in cases:
                with self.subTest(name=name):
                    input_path = Path(directory) / f"{name}.json"
                    write_json(input_path, document)
                    with self.assertRaisesRegex(iaf.IAFTitleAbstractError, message):
                        iaf.match_json(DICTIONARY_PATH, MATCHER_PATH, input_path)

    def test_synthetic_direct_records_are_explicitly_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "synthetic.json"
            write_json(
                input_path,
                {
                    "records": [
                        {
                            "record_id": "synthetic-direct-1",
                            "title": "CubeSat MBSE",
                            "abstract": None,
                        }
                    ]
                },
            )
            with self.assertRaisesRegex(
                iaf.IAFTitleAbstractError, "--synthetic-direct-records"
            ):
                iaf.match_json(DICTIONARY_PATH, MATCHER_PATH, input_path)
            report = iaf.match_json(
                DICTIONARY_PATH,
                MATCHER_PATH,
                input_path,
                synthetic_direct_records=True,
            )

        self.assertEqual(report["input_mode"], "synthetic_direct_records")
        self.assertEqual(report["records"][0]["record_id"], "synthetic-direct-1")

    def test_synthetic_mode_also_rejects_missing_and_duplicate_record_ids(self) -> None:
        cases = (
            (
                {"records": [{"title": "CubeSat MBSE", "abstract": None}]},
                "non-empty stable record_id",
            ),
            (
                {
                    "records": [
                        {
                            "record_id": "synthetic-duplicate",
                            "title": "CubeSat MBSE",
                            "abstract": None,
                        },
                        {
                            "record_id": "synthetic-duplicate",
                            "title": "CubeSat MBSE",
                            "abstract": None,
                        },
                    ]
                },
                "duplicate stable record_id",
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            for index, (document, message) in enumerate(cases):
                with self.subTest(index=index):
                    input_path = Path(directory) / f"synthetic-{index}.json"
                    write_json(input_path, document)
                    with self.assertRaisesRegex(iaf.IAFTitleAbstractError, message):
                        iaf.match_json(
                            DICTIONARY_PATH,
                            MATCHER_PATH,
                            input_path,
                            synthetic_direct_records=True,
                        )


class LocalTagContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matcher_module, cls.matcher = iaf.make_matcher(DICTIONARY_PATH, MATCHER_PATH)

    def match(self, record: dict[str, object], record_id: str) -> dict[str, object]:
        return iaf.match_iaf_title_abstract_record(
            self.matcher_module, self.matcher, record, record_id=record_id
        )

    def test_t2_requires_a_token_bounded_model_or_architecture_anchor(self) -> None:
        uncoupled = self.match(
            {
                "title": "CubeSat MBSE",
                "abstract": "The workflow was tailored.",
            },
            "synthetic-uncoupled",
        )
        coupled = self.match(
            {
                "title": "CubeSat MBSE tailored workflow",
                "abstract": "The model is maintained separately.",
            },
            "synthetic-coupled",
        )
        substring = self.match(
            {
                "title": "CubeSat MBSE tailored workflow",
                "abstract": "The architectureless note is maintained.",
            },
            "synthetic-substring",
        )

        self.assertTrue(uncoupled["tags"]["iaf_b_core"])
        self.assertFalse(uncoupled["tags"]["iaf_t2_tag"])
        self.assertEqual(uncoupled["t2_coupling_anchor_fields"], [])
        self.assertTrue(coupled["tags"]["iaf_t2_tag"])
        self.assertEqual(coupled["t2_coupling_anchor_fields"], ["abstract"])
        self.assertFalse(substring["tags"]["iaf_t2_tag"])
        self.assertEqual(substring["t2_coupling_anchor_fields"], [])

    def test_high_specificity_and_broad_m_plus_r_subtypes_are_distinct(self) -> None:
        high = self.match(
            {
                "title": "CubeSat MBSE overview",
                "abstract": "A complete public abstract is supplied.",
            },
            "synthetic-high",
        )
        broad_relation = self.match(
            {
                "title": "CubeSat overview",
                "abstract": "The system model traces requirements.",
            },
            "synthetic-broad-relation",
        )
        broad_without_relation = self.match(
            {
                "title": "CubeSat overview",
                "abstract": "The system model is maintained.",
            },
            "synthetic-broad-no-relation",
        )

        self.assertTrue(high["tags"]["iaf_high_specificity_m_tag"])
        self.assertFalse(high["tags"]["iaf_broad_m_plus_r_tag"])
        self.assertFalse(broad_relation["tags"]["iaf_high_specificity_m_tag"])
        self.assertTrue(broad_relation["tags"]["iaf_broad_m_plus_r_tag"])
        self.assertFalse(broad_without_relation["tags"]["iaf_broad_m_plus_r_tag"])


class FixtureAndCliTests(unittest.TestCase):
    def test_strict_fixture_suite_passes_and_rejects_an_omitted_hit(self) -> None:
        report = iaf.run_fixtures(DICTIONARY_PATH, MATCHER_PATH, FIXTURE_PATH)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["fixture_count"], 19)

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        fixture["fixtures"][0]["expected"]["field_term_ids"]["title"].remove(
            "T_REUSE"
        )
        with tempfile.TemporaryDirectory() as directory:
            altered_path = Path(directory) / "altered-fixture.json"
            write_json(altered_path, fixture)
            altered = iaf.run_fixtures(DICTIONARY_PATH, MATCHER_PATH, altered_path)
        self.assertEqual(altered["status"], "failed")
        self.assertIn("expected exact term ids", altered["cases"][0]["errors"][0])

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        fixture["fixtures"][0]["expected"]["tags"]["iaf_t2_tag"] = False
        with tempfile.TemporaryDirectory() as directory:
            altered_path = Path(directory) / "altered-tag-fixture.json"
            write_json(altered_path, fixture)
            altered = iaf.run_fixtures(DICTIONARY_PATH, MATCHER_PATH, altered_path)
        self.assertEqual(altered["status"], "failed")
        self.assertIn("iaf_t2_tag expected", altered["cases"][0]["errors"][0])

    def test_cli_writes_adapter_result_and_preserves_existing_output_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "adapter.json"
            output_path = root / "result.json"
            stable_id = "iaf-digital-library:IAC-2024:cli-001"
            write_json(input_path, {"results": [adapter_record(stable_id)]})
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = iaf.main(
                    [
                        "--dictionary",
                        str(DICTIONARY_PATH),
                        "--matcher",
                        str(MATCHER_PATH),
                        "match-json",
                        "--input",
                        str(input_path),
                        "--output-path",
                        str(output_path),
                    ]
                )
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["records"][0]["record_id"],
                stable_id,
            )
            self.assertIn('"status": "success"', stdout.getvalue())

            original = b'{"preserved": true}\n'
            output_path.write_bytes(original)
            write_json(
                input_path,
                {
                    "results": [
                        adapter_record("iaf-digital-library:IAC-2024:duplicate"),
                        adapter_record("iaf-digital-library:IAC-2024:duplicate"),
                    ]
                },
            )
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = iaf.main(
                    [
                        "--dictionary",
                        str(DICTIONARY_PATH),
                        "--matcher",
                        str(MATCHER_PATH),
                        "match-json",
                        "--input",
                        str(input_path),
                        "--output-path",
                        str(output_path),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertEqual(output_path.read_bytes(), original)
            self.assertIn("duplicate stable paperId", stderr.getvalue())

    def test_atomic_write_leaves_an_existing_artifact_intact_on_serialization_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "result.json"
            original = b'{"preserved": true}\n'
            output_path.write_bytes(original)
            with mock.patch.object(iaf.json, "dump", side_effect=TypeError("synthetic")):
                with self.assertRaises(TypeError):
                    iaf.atomic_write_json(output_path, {"status": "replacement"})
            self.assertEqual(output_path.read_bytes(), original)
            self.assertEqual(list(Path(directory).glob(".result.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
