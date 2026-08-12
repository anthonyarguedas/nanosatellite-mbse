"""Offline privacy and frozen-contract regressions for API pagination reconciliation."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from urllib.parse import quote_plus
from unittest.mock import patch

import api_pagination_reconcile as reconcile


MARKER = "SYNTHETIC_URL_REDACTION_MARKER"


def encoded(value: str, times: int) -> str:
    """Produce a synthetic nested URL component without contacting a source."""
    for _ in range(times):
        value = quote_plus(value)
    return value


def scopus_entry(identifier: str, **extra: object) -> dict[str, object]:
    """Return the smallest synthetic Scopus-like record accepted by the parser."""
    return {"eid": identifier, "citedby-count": "0", **extra}


def scopus_response(
    total: int,
    start: int,
    page_size: int,
    entries: list[dict[str, object]],
) -> dict[str, object]:
    """Build an in-memory Scopus response fixture only."""
    return {
        "search-results": {
            "opensearch:totalResults": str(total),
            "opensearch:startIndex": str(start),
            "opensearch:itemsPerPage": str(page_size),
            "entry": entries,
        }
    }


def ieee_zero_response() -> dict[str, object]:
    """Build the documented synthetic IEEE one-empty-page convention."""
    return {
        "totalRecords": 0,
        "startRecord": 0,
        "endRecord": 0,
        "recordsPerPage": 25,
        "totalPages": 1,
        "records": [],
    }


def execution_args(source: str) -> Namespace:
    """Return validated, non-networking arguments for execute_pass fixtures."""
    return Namespace(
        source=source,
        query="synthetic offline query",
        page_size=25,
        classification="pilot_not_candidate_search",
        timeout=1.0,
        retries=0,
        backoff_seconds=0.0,
        page_delay_seconds=0.0,
        scopus_api_key_env="SYNTHETIC_UNUSED_ENV",
        scopus_sort="eid",
        ieee_year_start=2011,
        ieee_year_end=2026,
        ieee_content_types=[],
        ieee_language="English",
        ieee_sort_type="newest",
    )


class MarkerAssertions(unittest.TestCase):
    """Shared assertions that never print the synthetic marker on failure."""

    def assert_marker_absent(self, value: object) -> None:
        if isinstance(value, str):
            rendered = value
        else:
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if MARKER in rendered:
            self.fail("synthetic marker survived redaction")


class SensitiveUrlRedactionTests(MarkerAssertions):
    def test_benign_query_and_near_names_are_preserved(self) -> None:
        with_sensitive = (
            "https://example.invalid/download?download=1&filename=report.pdf"
            f"&sid={MARKER}&csrf_token={MARKER}"
        )
        rendered = reconcile.redacted_url(with_sensitive)
        self.assert_marker_absent(rendered)
        self.assertEqual(
            rendered,
            "https://example.invalid/download?download=1&filename=report.pdf",
        )

        value = (
            "https://example.invalid/download?download=1&filename=report.pdf"
            "&keywords=systems&sideline=archive&session_status=ready"
            "&tokenizer=plain&user_info_display=public"
        )
        rendered = reconcile.redacted_url(value)
        self.assertEqual(rendered, value)
        self.assert_marker_absent(rendered)

    def test_authority_userinfo_is_stripped(self) -> None:
        rendered = reconcile.redacted_url(
            f"https://synthetic-user:{MARKER}@example.invalid/document?download=1"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")
        self.assert_marker_absent(json.dumps(rendered))

    def test_encoded_and_nested_authority_userinfo_fail_closed(self) -> None:
        encoded_authority = (
            "https://synthetic-user%3A"
            f"{MARKER}%40example.invalid/document?download=1"
        )
        rendered = reconcile.redacted_url(encoded_authority)
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "")

        nested_authority = f"https://synthetic-user:{MARKER}@example.invalid/next"
        rendered = reconcile.redacted_url(
            "https://example.invalid/document?download=1&continue="
            f"{quote_plus(nested_authority)}"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")

    def test_malformed_url_fails_closed(self) -> None:
        malformed_values = (
            f"https://[not-a-host/?sid={MARKER}",
            f"https://example.invalid:not-a-port/document?continue={MARKER}",
        )
        for value in malformed_values:
            with self.subTest(value_type="malformed"):
                rendered = reconcile.redacted_url(value)
                self.assert_marker_absent(rendered)
                self.assertEqual(rendered, "")

    def test_routed_fragment_sensitive_context_is_dropped(self) -> None:
        rendered = reconcile.redacted_url(
            f"https://example.invalid/document?download=1#/route?sid={MARKER}"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")

    def test_direct_sensitive_fragment_is_dropped(self) -> None:
        rendered = reconcile.redacted_url(
            f"https://example.invalid/document?download=1#access_token={MARKER}"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")

    def test_repeatedly_encoded_sensitive_context_fails_closed(self) -> None:
        for depth in (2, 9):
            with self.subTest(depth=depth):
                rendered = reconcile.redacted_url(
                    "https://example.invalid/document?continue="
                    f"{encoded('?sid=' + MARKER, depth)}"
                )
                self.assert_marker_absent(rendered)
                self.assertEqual(rendered, "https://example.invalid/document")

    def test_nested_encoded_context_inside_benign_parameter_is_dropped(self) -> None:
        nested_url = f"https://example.invalid/next?sid={MARKER}"
        rendered = reconcile.redacted_url(
            "https://example.invalid/document?download=1&continue="
            f"{quote_plus(nested_url)}"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")

    def test_encoded_fragment_context_is_dropped(self) -> None:
        rendered = reconcile.redacted_url(
            "https://example.invalid/document?download=1#"
            f"{encoded('?access_token=' + MARKER, 1)}"
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(rendered, "https://example.invalid/document?download=1")

    def test_relative_ieee_url_removes_expanded_sensitive_keys(self) -> None:
        rendered = reconcile.ieee_document_url(
            {
                "articleNumber": "synthetic-17",
                "documentLink": (
                    "/document/synthetic-17?arnumber=17"
                    f"&session={MARKER}&JSESSIONID={MARKER}&searchId={MARKER}"
                ),
            }
        )
        self.assert_marker_absent(rendered)
        self.assertEqual(
            rendered,
            "https://ieeexplore.ieee.org/document/synthetic-17?arnumber=17",
        )

    def test_scrubbed_values_are_safe_to_serialize_and_write(self) -> None:
        scrubbed = reconcile.scrub_sensitive(
            {
                "session": MARKER,
                "nested": {
                    "authority": (
                        f"https://synthetic-user:{MARKER}@example.invalid/document"
                    ),
                    "encoded": (
                        "https://example.invalid/document?continue="
                        f"{encoded('?sid=' + MARKER, 2)}"
                    ),
                    "malformed": f"https://[not-a-host/?sid={MARKER}",
                },
            }
        )
        self.assert_marker_absent(scrubbed)
        serialized = json.dumps(scrubbed, ensure_ascii=False)
        self.assert_marker_absent(serialized)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifact.json"
            reconcile.atomic_write_json(output, scrubbed)
            persisted = output.read_text(encoding="utf-8")
        self.assert_marker_absent(persisted)

    def test_end_to_end_artifacts_and_streams_do_not_retain_marker(self) -> None:
        nested_url = f"https://example.invalid/next?sid={MARKER}"
        nested_authority_url = f"https://synthetic-user:{MARKER}@example.invalid/next"
        response = scopus_response(
            1,
            0,
            1,
            [
                scopus_entry(
                    "synthetic-record-01",
                    **{
                        "prism:url": (
                            f"https://synthetic-user:{MARKER}@example.invalid/document"
                            "?download=1"
                        ),
                        "synthetic_urls": {
                            "malformed": f"https://[not-a-host/?sid={MARKER}",
                            "routed_fragment": (
                                "https://example.invalid/document#/route?"
                                f"sid={MARKER}"
                            ),
                            "repeated": (
                                "https://example.invalid/document?continue="
                                f"{encoded('?sid=' + MARKER, 2)}"
                            ),
                            "nested": (
                                "https://example.invalid/document?continue="
                                f"{quote_plus(nested_url)}"
                            ),
                            "nested_authority": (
                                "https://example.invalid/document?continue="
                                f"{quote_plus(nested_authority_url)}"
                            ),
                            "encoded_fragment": (
                                "https://example.invalid/document#"
                                f"{encoded('?access_token=' + MARKER, 1)}"
                            ),
                        },
                    },
                )
            ],
        )
        calls: list[dict[str, object]] = []

        def fake_fetch_json(**kwargs: object) -> tuple[dict[str, object], list[dict[str, object]]]:
            calls.append(kwargs)
            return copy.deepcopy(response), []

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "private-output"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                patch.object(reconcile, "fetch_json", side_effect=fake_fetch_json),
                patch.object(reconcile, "scopus_auth_headers", return_value={"Accept": "application/json"}),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                result = reconcile.main(
                    [
                        "--source",
                        "scopus",
                        "--query",
                        "synthetic offline query",
                        "--output-dir",
                        str(output_dir),
                        "--page-size",
                        "25",
                        "--passes",
                        "2",
                        "--retries",
                        "0",
                        "--page-delay-seconds",
                        "0",
                        "--total-change-reruns",
                        "0",
                    ]
                )
            self.assertEqual(result, 0)
            self.assertEqual(len(calls), 2)
            self.assert_marker_absent(result)
            self.assert_marker_absent(stdout.getvalue())
            self.assert_marker_absent(stderr.getvalue())

            raw_path = output_dir / "snapshot-attempt-01/pass-01/page-0001.response.json"
            normalized_path = output_dir / "snapshot-attempt-01/pass-01/normalized-results.json"
            self.assertTrue(raw_path.is_file())
            self.assertTrue(normalized_path.is_file())
            for path in output_dir.rglob("*"):
                if path.is_file():
                    text = path.read_text(encoding="utf-8")
                    self.assert_marker_absent(text)
                    self.assert_marker_absent(json.loads(text))
            normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
            self.assertEqual(
                normalized["results"][0]["url"],
                "https://example.invalid/document?download=1",
            )

    def test_network_failure_does_not_emit_marker_in_errors_or_artifacts(self) -> None:
        request_error = reconcile.requests.ConnectionError(
            f"synthetic connection failure https://example.invalid/?sid={MARKER}"
        )
        with patch.object(reconcile.requests, "get", side_effect=request_error):
            with self.assertRaises(reconcile.ReconciliationError) as raised:
                reconcile.fetch_json(
                    source="scopus",
                    method="GET",
                    endpoint="https://example.invalid/",
                    headers={},
                    params={"query": "synthetic"},
                    payload=None,
                    timeout_seconds=1,
                    retries=0,
                    backoff_seconds=0,
                )
        self.assert_marker_absent(str(raised.exception))

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "failure-output"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                patch.object(reconcile.requests, "get", side_effect=request_error),
                patch.object(reconcile, "scopus_auth_headers", return_value={"Accept": "application/json"}),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                result = reconcile.main(
                    [
                        "--source",
                        "scopus",
                        "--query",
                        "synthetic offline query",
                        "--output-dir",
                        str(output_dir),
                        "--page-size",
                        "25",
                        "--retries",
                        "0",
                        "--page-delay-seconds",
                        "0",
                    ]
                )
            self.assertEqual(result, 1)
            self.assert_marker_absent(result)
            self.assert_marker_absent(stdout.getvalue())
            self.assert_marker_absent(stderr.getvalue())
            for path in output_dir.rglob("*"):
                if path.is_file():
                    self.assert_marker_absent(path.read_text(encoding="utf-8"))


class FrozenContractRegressionTests(unittest.TestCase):
    def test_frozen_public_request_construction_is_unchanged(self) -> None:
        scopus = reconcile.scopus_public_request("synthetic query", 25, 25, "eid")
        self.assertEqual(scopus["method"], "GET")
        self.assertEqual(scopus["endpoint"], reconcile.SCOPUS_ENDPOINT)
        self.assertEqual(scopus["headers"], {
            "Accept": "application/json",
            "X-ELS-APIKey": "not_serialized; supplied only from secure runtime environment",
        })
        self.assertEqual(
            scopus["query_parameters"],
            {
                "query": "synthetic query",
                "count": "25",
                "start": "25",
                "view": "COMPLETE",
                "sort": "eid",
                "httpAccept": "application/json",
            },
        )

        ieee = reconcile.ieee_public_request(
            "synthetic query",
            2,
            25,
            2011,
            2026,
            ["Journals", "Books"],
            "English",
            "newest",
        )
        self.assertEqual(ieee["method"], "POST")
        self.assertEqual(ieee["endpoint"], reconcile.IEEE_ENDPOINT)
        self.assertEqual(ieee["headers"], reconcile.IEEE_HEADERS)
        self.assertEqual(
            ieee["json_body"],
            {
                "action": "search",
                "newsearch": True,
                "matchBoolean": True,
                "matchPubs": True,
                "queryText": "synthetic query",
                "highlight": False,
                "returnType": "SEARCH",
                "rowsPerPage": 25,
                "pageNumber": 2,
                "sortType": "newest",
                "ranges": ["2011_2026_Year"],
                "refinements": [
                    "ContentType:Journals",
                    "ContentType:Books",
                    "Language:English",
                ],
            },
        )
        no_type_filter = reconcile.ieee_public_request(
            "synthetic query", 1, 25, 2011, 2026, [], "English", "newest"
        )
        self.assertEqual(no_type_filter["json_body"]["refinements"], ["Language:English"])

    def test_parsers_accept_scopus_terminal_and_ieee_zero_conventions(self) -> None:
        terminal = reconcile.parse_scopus_page(
            scopus_response(1, 0, 1, [scopus_entry("synthetic-terminal")]),
            expected_start=0,
        )
        self.assertEqual(terminal.total, 1)
        self.assertEqual(terminal.server_page_size, 1)
        self.assertEqual(terminal.identifiers, ["synthetic-terminal"])

        zero = reconcile.parse_ieee_page(ieee_zero_response(), expected_start=0, expected_page_size=25)
        self.assertEqual(zero.total, 0)
        self.assertEqual(zero.server_page_size, 25)
        self.assertEqual(zero.records, [])

    def test_scopus_terminal_pagination_reconciliation_is_unchanged(self) -> None:
        first_entries = [scopus_entry(f"synthetic-id-{index:02d}") for index in range(25)]
        terminal_entry = [scopus_entry("synthetic-id-25")]
        responses = {
            0: scopus_response(26, 0, 25, first_entries),
            25: scopus_response(26, 25, 1, terminal_entry),
        }
        requested_positions: list[int] = []

        def fake_fetch_json(**kwargs: object) -> tuple[dict[str, object], list[dict[str, object]]]:
            params = kwargs["params"]
            self.assertIsInstance(params, dict)
            position = int(str(params["start"]))
            requested_positions.append(position)
            return copy.deepcopy(responses[position]), []

        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(reconcile, "fetch_json", side_effect=fake_fetch_json),
                patch.object(reconcile, "scopus_auth_headers", return_value={"Accept": "application/json"}),
            ):
                reconciliation = reconcile.execute_pass(
                    execution_args("scopus"), Path(directory) / "pass-01", 1
                )
        self.assertEqual(requested_positions, [0, 25])
        self.assertEqual(reconciliation["source_total"], 26)
        self.assertEqual(reconciliation["expected_pages"], 2)
        self.assertEqual(reconciliation["retrieved_records"], 26)
        self.assertTrue(reconciliation["retrieved_equals_source_total"])
        self.assertEqual(reconciliation["pages"][1]["observed"]["reported_items_per_page"], 1)

    def test_ieee_zero_pagination_reconciliation_is_unchanged(self) -> None:
        requested_pages: list[int] = []

        def fake_fetch_json(**kwargs: object) -> tuple[dict[str, object], list[dict[str, object]]]:
            payload = kwargs["payload"]
            self.assertIsInstance(payload, dict)
            requested_pages.append(int(payload["pageNumber"]))
            return copy.deepcopy(ieee_zero_response()), []

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(reconcile, "fetch_json", side_effect=fake_fetch_json):
                reconciliation = reconcile.execute_pass(
                    execution_args("ieee"), Path(directory) / "pass-01", 1
                )
        self.assertEqual(requested_pages, [1])
        self.assertEqual(reconciliation["source_total"], 0)
        self.assertEqual(reconciliation["expected_pages"], 1)
        self.assertEqual(reconciliation["pages_retrieved"], 1)
        self.assertEqual(reconciliation["retrieved_records"], 0)
        self.assertTrue(reconciliation["retrieved_equals_source_total"])


if __name__ == "__main__":
    unittest.main()
