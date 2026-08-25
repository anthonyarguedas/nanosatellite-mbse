#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.0"]
# ///

"""Focused offline tests for the SLR1 ESA Indico local-harvest helper."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from urllib.error import HTTPError

SCRIPT = Path(__file__).with_name("esa_indico_local_harvest.py")
SPEC = importlib.util.spec_from_file_location("esa_indico_local_harvest", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ESAIndicoPilotArtifactTests(unittest.TestCase):
    def test_manifest_validates_against_shared_pilot_schema(self) -> None:
        import jsonschema

        root = Path(__file__).resolve().parents[1]
        schema_path = root / "searches" / "schemas" / "pilot-manifest.schema.json"
        pilot_root = root / "searches" / "sources" / "s-l02-esa-indico" / "pilots"
        with schema_path.open(encoding="utf-8") as handle:
            schema = json.load(handle)
        manifests = sorted(pilot_root.glob("S-L02-P*/manifest.json"))
        self.assertTrue(manifests)
        for manifest_path in manifests:
            with manifest_path.open(encoding="utf-8") as handle:
                manifest = json.load(handle)
            jsonschema.Draft202012Validator(schema).validate(manifest)


class ESAIndicoLocalMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dictionary = MODULE.load_dictionary(MODULE.default_dictionary_path())

    def document(self, document_id: str, fields: dict[str, str]) -> dict[str, object]:
        return {
            "document_id": document_id,
            "source_object_id": document_id.removesuffix(":metadata"),
            "route_type": "test_terminal_text",
            "candidate_eligible": True,
            "fields": fields,
        }

    def test_ordered_phrase_and_hyphen_normalization_are_local_and_deterministic(
        self,
    ) -> None:
        result = MODULE.match_one_document(
            self.document("d1", {"title": "Cube-Sat model-based systems engineering"}),
            self.dictionary,
        )
        self.assertIn("core_B", result["candidate_partitions"])
        self.assertTrue(result["concepts"]["P"]["matched"])
        self.assertTrue(result["concepts"]["M_H"]["matched"])

    def test_acronym_does_not_match_a_substring(self) -> None:
        hits = MODULE.phrase_hits({"text": "xMBSE MBSE MBSEs"}, "MBSE")
        self.assertEqual([(hit.start, hit.end) for hit in hits], [(1, 2)])

    def test_required_concepts_cannot_combine_across_document_routes(self) -> None:
        output = MODULE.match_documents(
            [
                self.document("event:1:contribution:1:metadata", {"title": "CubeSat"}),
                self.document("event:1:contribution:2:metadata", {"title": "MBSE"}),
            ],
            self.dictionary,
        )
        self.assertEqual(output["candidate_document_route_count"], 0)
        self.assertEqual(output["candidate_source_object_count"], 0)

    def test_defined_metadata_route_can_use_its_own_title_and_description(self) -> None:
        result = MODULE.match_one_document(
            self.document(
                "event:1:contribution:1:metadata",
                {"title": "CubeSat", "description": "Model based systems engineering"},
            ),
            self.dictionary,
        )
        self.assertIn("core_B", result["candidate_partitions"])

    def test_metadata_match_is_diagnostic_not_a_candidate_without_terminal_text(self) -> None:
        metadata = self.document(
            "event:1:contribution:1:metadata",
            {"title": "CubeSat model based systems engineering"},
        )
        metadata["candidate_eligible"] = False
        output = MODULE.match_documents([metadata], self.dictionary)
        self.assertEqual(output["candidate_document_route_count"], 0)
        self.assertEqual(output["raw_matching_document_route_count"], 1)
        self.assertEqual(output["noncandidate_metadata_match_count"], 1)
        self.assertEqual(output["documents"][0]["raw_candidate_partitions"], ["core_B"])
        self.assertEqual(output["documents"][0]["candidate_partitions"], [])

    def test_pair_rule_accepts_five_intervening_tokens_and_rejects_six(self) -> None:
        within = MODULE.match_one_document(
            self.document(
                "within",
                {"text": "CubeSat system model one two three four five tailor"},
            ),
            self.dictionary,
        )
        outside = MODULE.match_one_document(
            self.document(
                "outside",
                {"text": "CubeSat system model one two three four five six tailor"},
            ),
            self.dictionary,
        )
        self.assertTrue(within["tags"]["T2_tag"])
        self.assertTrue(within["tags"]["BT2_equivalent_tag"])
        self.assertFalse(outside["tags"]["T2_tag"])
        self.assertFalse(outside["tags"]["BT2_equivalent_tag"])

    def test_artifact_architecture_does_not_supply_independent_r(self) -> None:
        result = MODULE.match_one_document(
            self.document(
                "d1", {"text": "CubeSat system model reference architecture"}
            ),
            self.dictionary,
        )
        self.assertIn("BG2", result["candidate_partitions"])
        self.assertFalse(result["tags"]["R_tag"])
        self.assertFalse(result["tags"]["B2_equivalent_tag"])
        self.assertEqual(
            len(result["concepts"]["R"]["suppressed_architecture_hits"]), 1
        )

    def test_ordered_phrase_cannot_cross_separate_keyword_values(self) -> None:
        fields = MODULE.metadata_fields(
            {"keywords": ["model-based", "systems", "engineering"]}
        )
        self.assertFalse(MODULE.phrase_hits(fields, "model based systems engineering"))


class ESAIndicoRouteTests(unittest.TestCase):
    def test_search_probe_preserves_minus_one_as_unavailable_not_zero(self) -> None:
        class FakeClient:
            def get_json(self, url):
                self.url = url
                return (
                    {
                        "total": -1,
                        "results": [
                            {
                                "type": "contribution",
                                "event_id": 472,
                                "contribution_id": 9142,
                            }
                        ],
                        "pagenav": {"next": 10},
                    },
                    {
                        "request_path": "/search/api/search",
                        "observed_at": "2026-08-23T00:00:00-04:00",
                    },
                )

        result = MODULE.probe_public_search(
            FakeClient(), query="MBSE", result_type="contributions"
        )
        self.assertIsNone(result["source_reported_total"])
        self.assertEqual(
            result["source_reported_total_status"], "unavailable_minus_one"
        )
        self.assertTrue(result["next_page_present"])
        self.assertEqual(
            result["rows"][0]["stable_result_id"], "event:472:contribution:9142"
        )

    def test_category_ledger_names_the_requested_nonroot_category(self) -> None:
        class FakeClient:
            def get_json(self, _url):
                return (
                    {
                        "count": 1,
                        "results": [
                            {
                                "id": "472",
                                "categoryId": "5",
                                "url": "https://indico.esa.int/event/472/",
                                "startDate": {"date": "2023-11-16"},
                                "endDate": {"date": "2023-11-16"},
                            }
                        ],
                    },
                    {"response_sha256": "a" * 64},
                )

        ledger = MODULE.enumerate_category_window(
            FakeClient(), category_id="5", from_date="2023-11-01", to_date="2023-11-30"
        )
        self.assertEqual(ledger["source_boundary"], "public ESA Indico category-5 export only")
        self.assertEqual(ledger["source_complete_flag_status"], "absent_or_null")

    def test_category_reconciliation_requires_identical_repeated_inputs(self) -> None:
        base = {
            "ledger_schema_version": "esa-indico-category-window/v1",
            "category_id": "0",
            "from_date": "2023-11-01",
            "to_date": "2023-11-30",
            "source_reported_total": 1,
            "retrieved_total": 1,
            "totals_reconciled": True,
            "source_complete_flag_status": "absent_or_null",
            "event_rows": [{"event_id": "472"}],
            "receipt": {"response_sha256": "a" * 64},
        }
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            output = Path(directory) / "out.json"
            MODULE.write_json(first, base)
            MODULE.write_json(second, base)
            args = SimpleNamespace(
                ledger_path=[str(first), str(second)], output_path=str(output)
            )
            self.assertEqual(MODULE.cmd_reconcile_category_windows(args), 0)
            result = MODULE.load_json(output)
            self.assertTrue(
                result["invariants"]["repeated_input_count_order_hash_and_complete_flag_match"]
            )
            changed = {**base, "receipt": {"response_sha256": "b" * 64}}
            MODULE.write_json(second, changed)
            self.assertEqual(MODULE.cmd_reconcile_category_windows(args), 2)

    def test_pdf_stage_refuses_a_limit_below_the_complete_ledger_before_download(
        self,
    ) -> None:
        attachment = {
            "classification": "public_pdf_pending_text",
            "attachment_id": "1",
            "event_id": "472",
            "download_url": "https://indico.esa.int/event/472/attachments/1/1/test.pdf",
            "owner_kind": "event",
            "owner_id": "472",
        }
        with self.assertRaises(MODULE.InputError):
            MODULE.process_public_pdf_routes(
                object(),
                [attachment],
                secure_dir=Path("/definitely/not/used"),
                max_pdf_downloads=0,
            )

    def test_direct_attachment_path_has_stable_ids(self) -> None:
        parsed = MODULE.direct_attachment_from_url(
            "/event/472/contributions/9150/attachments/5817/9769/RM_Model-Based%20for%20System%20Engineering%20-%20v2.2.pdf"
        )
        self.assertEqual(parsed["event_id"], "472")
        self.assertEqual(parsed["contribution_id"], "9150")
        self.assertEqual(parsed["attachment_id"], "9769")
        self.assertEqual(parsed["route_path"].split("/")[-2], "9769")

    def test_static_html_link_parser_deduplicates_and_filters_event(self) -> None:
        body = """
        <a href='/event/472/contributions/9150/attachments/5817/9700/a.pdf'>a</a>
        <a href='/event/472/contributions/9150/attachments/5817/9700/a.pdf'>a again</a>
        <a href='/event/407/attachments/4844/7416/b.pdf'>other event</a>
        """
        links = MODULE.extract_attachment_links(body, "472")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["attachment_id"], "9700")

    def test_event_export_parser_keeps_event_and_contribution_materials_separate(
        self,
    ) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "title": "Event",
                    "description": "",
                    "keywords": [],
                    "folders": [
                        {
                            "attachments": [
                                {
                                    "id": 1,
                                    "download_url": "https://indico.esa.int/event/472/attachments/10/1/event.pdf",
                                    "filename": "event.pdf",
                                    "content_type": "application/pdf",
                                    "is_protected": False,
                                }
                            ]
                        }
                    ],
                    "contributions": [
                        {
                            "db_id": 9150,
                            "url": "https://indico.esa.int/event/472/contributions/9150/",
                            "title": "Contribution",
                            "description": "",
                            "keywords": [],
                            "folders": [
                                {
                                    "attachments": [
                                        {
                                            "id": 2,
                                            "download_url": "https://indico.esa.int/event/472/contributions/9150/attachments/11/2/contribution.pdf",
                                            "filename": "contribution.pdf",
                                            "content_type": "application/pdf",
                                            "is_protected": False,
                                        }
                                    ]
                                }
                            ],
                            "subcontributions": [],
                        }
                    ],
                }
            ],
        }
        _, contributions, subs, attachments, documents = MODULE.parse_event_export(
            payload, "472"
        )
        self.assertEqual(contributions, [{"contribution_id": "9150"}])
        self.assertEqual(subs, [])
        self.assertEqual(attachments["1"]["owner_kind"], "event")
        self.assertEqual(attachments["2"]["owner_kind"], "contribution")
        self.assertEqual(len(documents), 4)

    def test_documented_subcontributions_route_and_field_are_parsed(self) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "title": "Event",
                    "contributions": [
                        {
                            "db_id": 9150,
                            "url": "https://indico.esa.int/event/472/contributions/9150/",
                            "title": "Contribution",
                            "subContributions": [
                                {
                                    "id": 77,
                                    "title": "Nested contribution",
                                    "subContributions": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        _, contributions, subs, _, documents = MODULE.parse_event_export(payload, "472")
        self.assertEqual(contributions, [{"contribution_id": "9150"}])
        self.assertEqual(
            subs,
            [
                {
                    "parent_contribution_id": "9150",
                    "subcontribution_id": "77",
                    "stable_id_scope": "event_parent_composite",
                }
            ],
        )
        self.assertIn(
            "event:472:contribution:9150:subcontribution:77:metadata",
            {document["document_id"] for document in documents},
        )
        self.assertIn("detail=subcontributions", MODULE.event_export_url("472"))

    def test_legacy_material_resources_preserve_event_and_contribution_owners(
        self,
    ) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "title": "Event",
                    "material": [
                        {
                            "id": 500,
                            "title": "Event legacy material",
                            "resources": [
                                {
                                    "id": 1,
                                    "name": "event-resource.pdf",
                                    "url": "https://indico.esa.int/event/472/attachments/10/1/event-resource.pdf",
                                }
                            ],
                        }
                    ],
                    "contributions": [
                        {
                            "db_id": 9150,
                            "url": "https://indico.esa.int/event/472/contributions/9150/",
                            "title": "Contribution",
                            "material": [
                                {
                                    "id": 501,
                                    "title": "Contribution legacy material",
                                    "resources": [
                                        {
                                            "id": 2,
                                            "name": "contribution-resource.pdf",
                                            "url": (
                                                "https://indico.esa.int/event/472/contributions/9150/"
                                                "attachments/11/2/contribution-resource.pdf"
                                            ),
                                        }
                                    ],
                                }
                            ],
                            "subContributions": [],
                        }
                    ],
                }
            ],
        }
        _, _, _, attachments, _ = MODULE.parse_event_export(payload, "472")
        self.assertEqual(attachments["1"]["owner_kind"], "event")
        self.assertEqual(attachments["1"]["owner_id"], "472")
        self.assertEqual(attachments["2"]["owner_kind"], "contribution")
        self.assertEqual(attachments["2"]["owner_id"], "9150")
        self.assertEqual(attachments["2"]["filename"], "contribution-resource.pdf")
        self.assertIn("legacy_material_resource", attachments["1"]["provenance"])
        self.assertTrue(
            attachments["1"]["download_url"].startswith("https://indico.esa.int/")
        )

    def test_harvest_refuses_an_attachment_prefix_before_owner_page_fetches(self) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "folders": [
                        {
                            "attachments": [
                                {
                                    "id": 1,
                                    "download_url": "https://indico.esa.int/event/472/attachments/10/1/event.pdf",
                                    "filename": "event.pdf",
                                    "is_protected": False,
                                }
                            ]
                        }
                    ],
                    "contributions": [],
                }
            ],
        }

        class FakeClient:
            def get_json(self, _url):
                return payload, {"request_path": "/export/event/472.json"}

            def get_html(self, _url):
                raise AssertionError("owner pages must not be fetched after a bound failure")

        with self.assertRaises(MODULE.CoverageError):
            MODULE.harvest_event(
                FakeClient(),
                event_id="472",
                dictionary={},
                max_contribution_pages=1,
                max_attachments=0,
                perform_matching=False,
            )

    def test_harvest_keeps_export_ids_separate_and_queues_non_pdf_and_static_only(
        self,
    ) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "title": "Event",
                    "folders": [
                        {
                            "attachments": [
                                {
                                    "id": 1,
                                    "download_url": "https://indico.esa.int/event/472/attachments/10/1/event.pdf",
                                    "filename": "event.pdf",
                                    "content_type": "application/pdf",
                                    "is_protected": False,
                                }
                            ]
                        }
                    ],
                    "contributions": [
                        {
                            "db_id": 9150,
                            "url": "https://indico.esa.int/event/472/contributions/9150/",
                            "title": "Contribution",
                            "folders": [
                                {
                                    "attachments": [
                                        {
                                            "id": 2,
                                            "download_url": (
                                                "https://indico.esa.int/event/472/contributions/9150/"
                                                "attachments/11/2/video.mp4"
                                            ),
                                            "filename": "video.mp4",
                                            "content_type": "video/mp4",
                                            "is_protected": False,
                                        },
                                        {
                                            "id": 4,
                                            "url": "https://external.invalid/material.txt",
                                            "filename": "material.txt",
                                            "content_type": "text/plain",
                                            "is_protected": False,
                                        },
                                    ]
                                }
                            ],
                            "subContributions": [],
                        }
                    ],
                }
            ],
        }

        class FakeClient:
            def get_json(self, _url):
                return payload, {
                    "request_path": "/export/event/472.json?detail=subcontributions"
                }

            def get_html(self, url):
                if "/contributions/9150/" in url:
                    return (
                        "<a href='/event/472/contributions/9150/attachments/11/2/video.mp4'>v</a>"
                        + "<a href='/event/472/contributions/9150/attachments/11/3/static.pdf'>s</a>",
                        {"request_path": "/event/472/contributions/9150/"},
                    )
                return (
                    "<a href='/event/472/attachments/10/1/event.pdf'>e</a>",
                    {"request_path": "/event/472/"},
                )

        ledger, _, _ = MODULE.harvest_event(
            FakeClient(),
            event_id="472",
            dictionary={},
            max_contribution_pages=1,
            perform_matching=False,
        )
        reconciliation = ledger["reconciliation"]
        self.assertEqual(reconciliation["export_attachment_ids"], ["1", "2", "4"])
        self.assertEqual(
            reconciliation["all_route_attachment_ids"], ["1", "2", "3", "4"]
        )
        self.assertEqual(reconciliation["static_only_attachment_ids"], ["3"])
        rows = {row["attachment_id"]: row for row in ledger["attachment_rows"]}
        self.assertEqual(
            rows["3"]["classification"], "direct_material_access_pending"
        )
        self.assertEqual(
            rows["2"]["classification"], "direct_material_access_pending"
        )
        self.assertEqual(
            rows["4"]["classification"], "irregular_or_external_pending_queue"
        )
        self.assertIsNone(rows["4"]["route_path"])
        queue_ids = {item["queue_id"] for item in ledger["manual_navigation_queue"]}
        self.assertIn("ESA-NAV-472-ACCESS-2", queue_ids)
        self.assertIn("ESA-NAV-472-IRREGULAR-4", queue_ids)
        self.assertIn("ESA-NAV-472-ACCESS-3", queue_ids)
        self.assertNotIn("ESA-NAV-472-PDF-3", queue_ids)
        self.assertFalse(ledger["material_route_coverage"]["coverage_complete"])

    def test_access_probe_distinguishes_public_non_pdf_from_a_pdf(self) -> None:
        class Response:
            status = 200
            headers = {"Content-Type": "video/mp4"}

            def getcode(self):
                return self.status

            def geturl(self):
                return "https://indico.esa.int/event/472/attachments/10/1/video.mp4"

            def read(self, _size=None):
                return b"binary-video-bytes"

            def close(self):
                pass

        class Opener:
            def open(self, _request, timeout):
                self.timeout = timeout
                return Response()

        client = MODULE.PublicClient(opener=Opener(), retries=0, min_request_interval=0)
        receipt = client.probe_access_status(
            "https://indico.esa.int/event/472/attachments/10/1/video.mp4"
        )
        self.assertEqual(receipt["access_status"], "public_non_pdf")
        self.assertEqual(receipt["observed_content_type"], "video/mp4")
        self.assertFalse(receipt["response_body_retained"])

    def test_probed_static_only_restriction_is_terminal_nonpublic_not_a_pdf(self) -> None:
        payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "title": "Event",
                    "contributions": [
                        {
                            "db_id": 9150,
                            "url": "https://indico.esa.int/event/472/contributions/9150/",
                            "title": "Contribution",
                            "folders": [
                                {
                                    "attachments": [
                                        {
                                            "id": 1,
                                            "download_url": "https://indico.esa.int/event/472/contributions/9150/attachments/11/1/export.pdf",
                                            "filename": "export.pdf",
                                            "content_type": "application/pdf",
                                            "is_protected": False,
                                        }
                                    ]
                                }
                            ],
                            "subContributions": [],
                        }
                    ],
                }
            ],
        }

        class FakeClient:
            def get_json(self, _url):
                return payload, {"request_path": "/export/event/472.json"}

            def get_html(self, url):
                if "/contributions/9150/" in url:
                    return (
                        "<a href='/event/472/contributions/9150/attachments/11/1/export.pdf'>e</a>"
                        "<a href='/event/472/contributions/9150/attachments/11/2/static.pdf'>s</a>",
                        {"request_path": "/event/472/contributions/9150/"},
                    )
                return "", {"request_path": "/event/472/"}

            def probe_access_status(self, url):
                if "/1/" in url:
                    return {
                        "access_status": "public_pdf",
                        "request_path": MODULE.route_path(url),
                        "http_status": 200,
                    }
                return {
                    "access_status": "access_restricted_or_login",
                    "request_path": MODULE.route_path(url),
                    "http_status": 302,
                }

        ledger, _, _ = MODULE.harvest_event(
            FakeClient(),
            event_id="472",
            dictionary={},
            max_contribution_pages=1,
            perform_matching=False,
            probe_material_access=True,
        )
        rows = {row["attachment_id"]: row for row in ledger["attachment_rows"]}
        self.assertEqual(rows["1"]["classification"], "public_pdf_pending_text")
        self.assertEqual(rows["2"]["classification"], "restricted_not_public_terminal")
        self.assertEqual(
            rows["2"]["source_boundary_disposition"],
            "excluded_nonpublic_restricted_or_login",
        )
        self.assertTrue(ledger["material_route_coverage"]["coverage_complete"])
        self.assertEqual(
            ledger["material_route_coverage"]["restricted_nonpublic_terminal_attachment_ids"],
            ["2"],
        )

    def test_declared_unprotected_access_conflict_fails_coverage_classification(self) -> None:
        record = {
            "is_protected": False,
            "route_status": "validated_direct_attachment",
            "access_status": "access_restricted_or_login",
        }
        self.assertEqual(
            MODULE.classify_attachment(record), "declared_public_access_conflict"
        )
        self.assertEqual(
            MODULE.attachment_boundary_disposition(
                record, "declared_public_access_conflict"
            ),
            "coverage_failure_declared_unprotected_but_anonymous_access_failed",
        )

    def test_pdf_stage_refuses_a_pdf_shaped_route_without_access_proof(self) -> None:
        attachment = {
            "classification": "direct_material_access_pending",
            "attachment_id": "1",
            "event_id": "472",
            "route_path": "/event/472/attachments/1/1/test.pdf",
            "owner_kind": "event",
            "owner_id": "472",
        }
        with self.assertRaises(MODULE.CoverageError):
            MODULE.process_public_pdf_routes(
                object(),
                [attachment],
                secure_dir=Path("/definitely/not/used"),
                max_pdf_downloads=1,
            )

    def test_dictionary_hash_lock_rejects_a_mismatch(self) -> None:
        with self.assertRaises(MODULE.CoverageError):
            MODULE.load_dictionary(
                MODULE.default_dictionary_path(), expected_sha256="0" * 64
            )

    def test_event_detail_inventory_compares_session_and_nested_routes(self) -> None:
        nested_payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "contributions": [
                        {"id": 1, "subContributions": []},
                        {"id": 2, "subContributions": []},
                    ],
                }
            ],
        }
        sessions_payload = {
            "count": 1,
            "results": [
                {
                    "id": "472",
                    "contributions": [{"id": 1, "subContributions": []}],
                    "sessions": [
                        {"contributions": [{"id": 2, "subContributions": []}]}
                    ],
                }
            ],
        }
        nested = MODULE.event_detail_inventory(
            nested_payload, "472", detail="subcontributions"
        )
        sessions = MODULE.event_detail_inventory(
            sessions_payload, "472", detail="sessions"
        )
        self.assertEqual(
            set(nested["contribution_ids_in_source_order"]),
            set(sessions["contribution_ids_in_source_order"]),
        )
        self.assertEqual(sessions["session_contribution_counts"], [1])

    def test_ocr_routes_strip_external_frontmatter_and_complete_only_exact_queue(self) -> None:
        coverage = {
            "required_confirmed_public_pdf_attachment_ids": ["7"],
            "failed_public_pdf_attachment_ids": [],
            "rows": [
                {
                    "attachment_id": "7",
                    "event_id": "472",
                    "owner_kind": "contribution",
                    "owner_id": "9150",
                    "pdf_sha256": "a" * 64,
                    "parse_state": "ocr_required",
                }
            ],
        }
        queue = [
            {
                "queue_id": "ESA-OCR-472-7",
                "action": "ocr_public_pdf_from_secure_checksum",
                "input": {"attachment_id": "7", "pdf_sha256": "a" * 64},
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            text_path = Path(directory) / "document.md"
            text_path.write_text(
                "---\nsource: /outside/git/source.pdf\n---\nCubeSat MBSE\n",
                encoding="utf-8",
            )
            with self.assertRaises(MODULE.CoverageError):
                MODULE.apply_ocr_text_routes(
                    coverage,
                    [],
                    queue,
                    {"7": text_path},
                    None,
                    receipt_bundle_sha256=None,
                )
            completion = {
                "7": {
                    "queue_id": "ESA-OCR-472-7",
                    "attachment_id": "7",
                    "pdf_sha256": "a" * 64,
                    "terminal_outcome": "ocr_text_extracted",
                    "completed_at": "2026-08-23T00:00:00-04:00",
                    "operator": {"type": "human", "identifier": "operator"},
                    "parser_or_ocr_route": "pdf_to_markdown.py --image-mode keep",
                    "matched_ocr_body_sha256": MODULE.sha256_text("CubeSat MBSE\n"),
                    "matched_ocr_body_utf8_bytes": len("CubeSat MBSE\n".encode("utf-8")),
                }
            }
            updated, documents, remaining = MODULE.apply_ocr_text_routes(
                coverage,
                [],
                queue,
                {"7": text_path},
                completion,
                receipt_bundle_sha256="c" * 64,
            )
        self.assertTrue(updated["coverage_complete"])
        self.assertEqual(updated["ocr_resolved_attachment_ids"], ["7"])
        self.assertEqual(remaining, [])
        self.assertEqual(documents[0]["fields"]["full_text"], "CubeSat MBSE\n")

    def test_non_pdf_queue_requires_terminal_text_route_not_a_silent_no_match(
        self,
    ) -> None:
        queue = [
            {
                "queue_id": "ESA-NAV-472-NONPDF-2",
                "action": "route_public_non_pdf_to_text_extractor_or_manual",
                "input": {"event_id": "472", "attachment_id": "2"},
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "text_sha256_or_failure_reason",
                ],
            }
        ]
        failed_receipt = {
            "receipt_schema_version": "esa-indico-manual-navigation-receipt/v1",
            "queue_id": "ESA-NAV-472-NONPDF-2",
            "outcome": "resolved",
            "terminal_outcome": "access_restricted_or_login",
            "completed_at": "2026-08-23T00:00:00-04:00",
            "operator": {"type": "human", "identifier": "operator"},
            "text_sha256_or_failure_reason": "access restricted",
            "observed_attachment_ids": ["2"],
            "observed_attachment_paths": [],
        }
        self.assertFalse(
            MODULE.validate_manual_receipts(queue, [failed_receipt])[
                "coverage_complete"
            ]
        )
        text_receipt = {**failed_receipt, "terminal_outcome": "manual_text_extracted"}
        self.assertTrue(
            MODULE.validate_manual_receipts(queue, [text_receipt])["coverage_complete"]
        )

    def test_irregular_queue_requires_a_terminal_text_route(self) -> None:
        queue = [
            {
                "queue_id": "ESA-NAV-472-IRREGULAR-4",
                "action": "resolve_irregular_or_external_material",
                "input": {"event_id": "472", "attachment_id": "4"},
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "text_sha256_or_failure_reason",
                ],
            }
        ]
        base = {
            "receipt_schema_version": "esa-indico-manual-navigation-receipt/v1",
            "queue_id": "ESA-NAV-472-IRREGULAR-4",
            "outcome": "resolved",
            "completed_at": "2026-08-23T00:00:00-04:00",
            "operator": {"type": "human", "identifier": "operator"},
            "text_sha256_or_failure_reason": "a" * 64,
            "observed_attachment_ids": ["4"],
            "observed_attachment_paths": [],
        }
        self.assertFalse(
            MODULE.validate_manual_receipts(
                queue, [{**base, "terminal_outcome": "unsupported_media_no_text_extractor"}]
            )["coverage_complete"]
        )
        self.assertTrue(
            MODULE.validate_manual_receipts(
                queue, [{**base, "terminal_outcome": "manual_text_extracted"}]
            )["coverage_complete"]
        )

    def test_subcontribution_receipt_requires_a_real_material_route(self) -> None:
        queue = [
            {
                "queue_id": "ESA-NAV-472-SUB-9150-77",
                "action": "inspect_public_subcontribution_route",
                "input": {
                    "event_id": "472",
                    "parent_contribution_id": "9150",
                    "subcontribution_id": "77",
                },
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "coverage_receipt_sha256",
                ],
            }
        ]
        receipt = {
            "receipt_schema_version": "esa-indico-manual-navigation-receipt/v1",
            "queue_id": "ESA-NAV-472-SUB-9150-77",
            "outcome": "resolved",
            "terminal_outcome": "route_enumerated_and_all_materials_terminal",
            "completed_at": "2026-08-23T00:00:00-04:00",
            "operator": {"type": "human", "identifier": "operator"},
            "coverage_receipt_sha256": "a" * 64,
            "observed_contribution_ids": [],
            "observed_attachment_ids": [],
            "observed_attachment_paths": [],
        }
        self.assertFalse(MODULE.validate_manual_receipts(queue, [receipt])["coverage_complete"])
        resolved = {
            **receipt,
            "observed_attachment_ids": ["9900"],
        }
        self.assertTrue(MODULE.validate_manual_receipts(queue, [resolved])["coverage_complete"])

    def test_no_redirect_3xx_is_safe_access_failure_and_closes_error_response(
        self,
    ) -> None:
        class TrackingHTTPError(HTTPError):
            def __init__(self) -> None:
                super().__init__(
                    "https://indico.esa.int/example",
                    302,
                    "Found",
                    {"Location": "https://indico.esa.int/login?session=do-not-retain"},
                    None,
                )
                self.was_closed = False

            def close(self) -> None:
                self.was_closed = True

        class ErrorOpener:
            def __init__(self, error: TrackingHTTPError) -> None:
                self.error = error

            def open(self, _request, timeout):
                self.timeout = timeout
                raise self.error

        access_error = TrackingHTTPError()
        client = MODULE.PublicClient(
            opener=ErrorOpener(access_error), retries=0, min_request_interval=0
        )
        receipt = client.probe_access_status(
            "https://indico.esa.int/event/472/attachments/10/1/event.pdf"
        )
        self.assertEqual(receipt["access_status"], "access_restricted_or_login")
        self.assertEqual(receipt["http_status"], 302)
        self.assertTrue(access_error.was_closed)
        self.assertNotIn("Location", json.dumps(receipt))
        self.assertNotIn("session=", json.dumps(receipt))

        get_error = TrackingHTTPError()
        get_client = MODULE.PublicClient(
            opener=ErrorOpener(get_error), retries=0, min_request_interval=0
        )
        with self.assertRaises(MODULE.AccessError):
            get_client.get(
                "https://indico.esa.int/event/472/attachments/10/1/event.pdf",
                accept="application/pdf",
            )
        self.assertTrue(get_error.was_closed)

    def test_manual_receipt_requires_queue_identity_and_valid_attachment_path(
        self,
    ) -> None:
        queue = [
            {
                "queue_id": "ESA-NAV-472-PDF-9694",
                "action": "download_and_extract_public_pdf",
                "input": {"event_id": "472", "attachment_id": "9694"},
                "expected_attachment_ids": ["9694"],
                "required_output": [
                    "terminal_outcome",
                    "completed_at",
                    "operator",
                    "pdf_sha256",
                    "text_sha256_or_ocr_receipt",
                ],
            }
        ]
        receipt = {
            "receipt_schema_version": "esa-indico-manual-navigation-receipt/v1",
            "queue_id": "ESA-NAV-472-PDF-9694",
            "outcome": "resolved",
            "terminal_outcome": "text_extracted",
            "completed_at": "2026-08-23T00:00:00-04:00",
            "operator": {"type": "human", "identifier": "operator"},
            "pdf_sha256": "a" * 64,
            "text_sha256_or_ocr_receipt": "b" * 64,
            "observed_attachment_ids": ["9694"],
            "observed_attachment_paths": [
                "/event/472/contributions/9142/attachments/5812/9694/example.pdf"
            ],
        }
        result = MODULE.validate_manual_receipts(queue, [receipt])
        self.assertTrue(result["coverage_complete"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
