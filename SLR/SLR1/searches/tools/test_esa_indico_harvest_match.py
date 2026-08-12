#!/usr/bin/env python3
"""Offline transport, URL, identity, and census tests for the ESA harvester."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

import esa_indico_harvest_match as harvester


class FakeResponse:
    """Small response double that makes close and redirect behavior observable."""

    def __init__(
        self,
        status_code: int,
        *,
        payload: object | None = None,
        content: bytes = b"",
        headers: dict[str, Any] | None = None,
        url: str = "https://indico.esa.int/synthetic",
    ) -> None:
        self.status_code = status_code
        self._payload = {} if payload is None else payload
        self.content = content
        self.headers = headers or {"Content-Type": "application/json"}
        self.url = url
        self.text = json.dumps(self._payload)
        self.history: list[object] = []
        self.close_calls = 0

    def json(self) -> object:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def iter_content(self, _: int):
        yield self.content

    def close(self) -> None:
        self.close_calls += 1


class FakeSession:
    """A queue-based session double that records request state at every hop."""

    def __init__(
        self,
        responses: list[FakeResponse],
        *,
        after_get: Callable[["FakeSession", FakeResponse], None] | None = None,
    ) -> None:
        self.responses = responses.copy()
        self.after_get = after_get
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.cookies = requests.cookies.RequestsCookieJar()
        self.headers: dict[str, str] = {}
        self.auth: object | None = None
        self.cookies_present_at_get: list[bool] = []
        self.cookie_headers_at_get: list[bool] = []
        self.authorization_headers_at_get: list[bool] = []

    def get(self, *args: object, **kwargs: object) -> FakeResponse:
        self.cookies_present_at_get.append(bool(self.cookies))
        self.cookie_headers_at_get.append(
            any(name.casefold() == "cookie" for name in self.headers)
        )
        self.authorization_headers_at_get.append(
            any(name.casefold() == "authorization" for name in self.headers)
        )
        self.calls.append((args, kwargs))
        response = self.responses.pop(0)
        if self.after_get:
            self.after_get(self, response)
        return response


class ESAHarvesterTransportTests(unittest.TestCase):
    def attachment(
        self,
        url: str = "https://indico.esa.int/file.pdf",
        *,
        transport_allowed: bool = True,
    ) -> harvester.Attachment:
        return harvester.Attachment(
            key="synthetic",
            association_type="event",
            event_id="1",
            contribution_id=None,
            folder_id="1",
            folder_title="",
            attachment_id="1",
            title="",
            description="",
            filename="file.pdf",
            content_type="application/pdf",
            size=None,
            url=url,
            protected=False,
            document_like=True,
            lead_only_hint=False,
            transport_allowed=transport_allowed,
        )

    def test_strict_origin_rejects_authority_variants_and_fragments(self) -> None:
        self.assertTrue(
            harvester.is_public_esa_url(
                "https://indico.esa.int/export/categ/0.json?detail=contributions"
            )
        )
        for value in (
            "HTTPS://indico.esa.int/export/categ/0.json",
            "https://INDICO.ESA.INT/export/categ/0.json",
            "https://user:secret@indico.esa.int/export/categ/0.json",
            "https://indico.esa.int:443/export/categ/0.json",
            "https://indico.esa.int:444/export/categ/0.json",
            "https://indico.esa.int.example.invalid/export/categ/0.json",
            "https://example.invalid/export/categ/0.json",
            "https://indico.esa.int/export/categ/0.json#fragment",
            "http://indico.esa.int/export/categ/0.json",
        ):
            self.assertFalse(harvester.is_public_esa_url(value), value)
            self.assertIsNone(harvester.canonical_public_esa_url(value)[0])
        rendered = harvester.safe_url(
            "https://user:secret@indico.esa.int/x?token=private#fragment"
        )
        self.assertNotIn("secret", rendered)
        self.assertNotIn("private", rendered)

    def test_benign_query_survives_but_sensitive_context_is_redacted_not_fetched(self) -> None:
        raw_url = (
            "https://indico.esa.int/file.pdf?download=1&filename=report%20copy.pdf"
            "&csrf_token=secret&X-CSRF-Token=xsecret&search-session=state&keywords=MBSE&token=private"
        )
        safe_url, transport_allowed = harvester.canonical_public_esa_url(raw_url)
        self.assertEqual(
            safe_url,
            "https://indico.esa.int/file.pdf?download=1&filename=report%20copy.pdf&keywords=MBSE",
        )
        self.assertFalse(transport_allowed)
        self.assertEqual(harvester.safe_url(raw_url), safe_url)
        self.assertNotIn("secret", safe_url)
        self.assertNotIn("private", safe_url)
        self.assertNotIn("xsecret", safe_url)

        owner = {
            "folders": [
                {
                    "id": 1,
                    "attachments": [
                        {"id": 1, "filename": "file.pdf", "download_url": raw_url}
                    ],
                }
            ]
        }
        attachment = next(iter(harvester.iter_materials(owner, "event", "1", None)))
        self.assertEqual(attachment.url, safe_url)
        self.assertFalse(attachment.transport_allowed)
        self.assertNotIn("secret", attachment.key)
        self.assertNotIn("private", attachment.key)
        session = FakeSession([])
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session, attachment, Path(temporary) / "file.pdf", 1, 0, 0
            )
        self.assertEqual(result["status"], "inaccessible_sensitive_url_context")
        self.assertEqual(session.calls, [])

    def test_benign_download_query_is_retained_for_the_actual_request(self) -> None:
        url = "https://indico.esa.int/file.pdf?download=1&filename=report%20copy.pdf"
        response = FakeResponse(200, content=b"document", url=url)
        session = FakeSession([response])
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session, self.attachment(url), Path(temporary) / "file.pdf", 1, 0, 0
            )
        self.assertTrue(result["retrieved"])
        self.assertEqual(session.calls[0][0][0], url)
        self.assertEqual(result["final_url"], url)
        self.assertEqual(response.close_calls, 1)

    def test_owned_session_and_each_request_clear_pre_and_post_response_state(self) -> None:
        client = harvester.anonymous_session({"Accept": "application/json"})
        try:
            self.assertFalse(client.trust_env)
            self.assertIsNone(client.auth)
            self.assertNotIn("Cookie", client.headers)
            self.assertNotIn("Authorization", client.headers)
        finally:
            client.close()

        def plant_state(session: FakeSession, _: FakeResponse) -> None:
            session.cookies.set("sid", "post-response", domain="indico.esa.int", path="/")
            session.headers["cookie"] = "sid=post-response"
            session.headers["authorization"] = "Bearer post-response"
            session.auth = "post-response"

        response = FakeResponse(200, payload={})
        session = FakeSession([response], after_get=plant_state)
        session.cookies.set("sid", "inherited", domain="indico.esa.int", path="/")
        session.headers["Cookie"] = "sid=inherited"
        session.headers["Authorization"] = "Bearer inherited"
        session.auth = "inherited"
        harvester.response_json(session, harvester.ROOT_URL, 1, 0, 0)
        self.assertFalse(session.cookies_present_at_get[0])
        self.assertFalse(session.cookie_headers_at_get[0])
        self.assertFalse(session.authorization_headers_at_get[0])
        self.assertFalse(session.cookies)
        self.assertFalse(any(name.casefold() == "cookie" for name in session.headers))
        self.assertFalse(any(name.casefold() == "authorization" for name in session.headers))
        self.assertIsNone(session.auth)
        self.assertFalse(session.calls[0][1]["allow_redirects"])
        self.assertEqual(response.close_calls, 1)

    def test_export_retry_closes_each_response_and_does_not_carry_cookie_state(self) -> None:
        first = FakeResponse(503)
        second = FakeResponse(200, payload={})

        def plant_cookie(session: FakeSession, _: FakeResponse) -> None:
            session.cookies.set("sid", "post-response", domain="indico.esa.int", path="/")

        session = FakeSession([first, second], after_get=plant_cookie)
        harvester.response_json(session, harvester.ROOT_URL, 1, 1, 0)
        self.assertEqual(first.close_calls, 1)
        self.assertEqual(second.close_calls, 1)
        self.assertEqual(session.cookies_present_at_get, [False, False])
        self.assertFalse(session.cookies)

    def test_export_redirect_and_noncanonical_response_are_fail_closed_and_closed(self) -> None:
        for response in (
            FakeResponse(302, headers={"Location": "/login"}),
            FakeResponse(200, url="https://user:secret@indico.esa.int/export/categ/0.json"),
        ):
            session = FakeSession([response])
            with self.assertRaises(harvester.HarvestError):
                harvester.response_json(session, harvester.ROOT_URL, 1, 0, 0)
            self.assertEqual(len(session.calls), 1)
            self.assertFalse(session.calls[0][1]["allow_redirects"])
            self.assertEqual(response.close_calls, 1)

    def test_attachment_follows_a_bounded_same_origin_redirect_and_closes_every_hop(self) -> None:
        first = FakeResponse(
            302,
            headers={"Location": "/download/file.pdf?download=1&filename=file.pdf"},
            url="https://indico.esa.int/file.pdf?download=1",
        )
        second_url = "https://indico.esa.int/download/file.pdf?download=1&filename=file.pdf"
        second = FakeResponse(200, content=b"document", url=second_url)
        session = FakeSession([first, second])
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session,
                self.attachment("https://indico.esa.int/file.pdf?download=1"),
                Path(temporary) / "file.pdf",
                1,
                0,
                0,
            )
        self.assertTrue(result["retrieved"])
        self.assertEqual(result["same_origin_redirects_followed"], 1)
        self.assertEqual(result["redirect_hops"], [{"hop": 1, "http_status": 302, "status": "followed_same_origin"}])
        self.assertEqual(
            [call[0][0] for call in session.calls],
            ["https://indico.esa.int/file.pdf?download=1", second_url],
        )
        self.assertTrue(all(call[1]["allow_redirects"] is False for call in session.calls))
        self.assertEqual(first.close_calls, 1)
        self.assertEqual(second.close_calls, 1)

    def test_attachment_refuses_unsafe_or_missing_redirect_targets_without_following(self) -> None:
        cases = {
            "https://example.invalid/file.pdf": "redirect_refused_non_public_origin",
            "https://user:secret@indico.esa.int/file.pdf": "redirect_refused_non_public_origin",
            "https://indico.esa.int:443/file.pdf": "redirect_refused_non_public_origin",
            "https://INDICO.ESA.INT/file.pdf": "redirect_refused_non_public_origin",
            "/file.pdf#fragment": "redirect_refused_non_public_origin",
            "/file.pdf?download=1&token=private": "redirect_refused_sensitive_context",
            "": "redirect_refused_missing_location",
        }
        for location, expected_status in cases.items():
            with self.subTest(location=location):
                headers = {"Location": location} if location else {"Content-Type": "application/json"}
                response = FakeResponse(302, headers=headers)
                session = FakeSession([response])
                with tempfile.TemporaryDirectory() as temporary:
                    result = harvester.download_attachment(
                        session,
                        self.attachment(),
                        Path(temporary) / "file.pdf",
                        1,
                        0,
                        0,
                    )
                self.assertEqual(result["status"], expected_status)
                self.assertFalse(result["retrieved"])
                self.assertEqual(len(session.calls), 1)
                self.assertEqual(response.close_calls, 1)
                self.assertNotIn("secret", json.dumps(result))
                self.assertNotIn("private", json.dumps(result))

    def test_attachment_redirect_loop_is_refused_and_all_responses_close(self) -> None:
        first = FakeResponse(302, headers={"Location": "/download/file.pdf"})
        second = FakeResponse(302, headers={"Location": "/file.pdf"})
        session = FakeSession([first, second])
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session, self.attachment(), Path(temporary) / "file.pdf", 1, 0, 0
            )
        self.assertEqual(result["status"], "redirect_loop_or_limit")
        self.assertEqual(len(session.calls), 2)
        self.assertEqual(result["redirect_hops"][-1]["status"], "redirect_loop_or_limit")
        self.assertEqual(first.close_calls, 1)
        self.assertEqual(second.close_calls, 1)

    def test_attachment_redirect_limit_is_bounded_and_closed(self) -> None:
        responses = [
            FakeResponse(302, headers={"Location": f"/hop-{number}.pdf"})
            for number in range(harvester.MAX_ATTACHMENT_REDIRECTS + 1)
        ]
        session = FakeSession(responses)
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session, self.attachment(), Path(temporary) / "file.pdf", 1, 0, 0
            )
        self.assertEqual(result["status"], "redirect_loop_or_limit")
        self.assertEqual(len(session.calls), harvester.MAX_ATTACHMENT_REDIRECTS + 1)
        self.assertTrue(all(response.close_calls == 1 for response in responses))

    def test_public_attachment_404_and_unsafe_material_are_explicit_coverage_outcomes(self) -> None:
        response = FakeResponse(404)
        session = FakeSession([response])
        with tempfile.TemporaryDirectory() as temporary:
            result = harvester.download_attachment(
                session, self.attachment(), Path(temporary) / "file.pdf", 1, 0, 0
            )
        self.assertEqual(result["status"], "http_404")
        self.assertFalse(result["retrieved"])
        self.assertEqual(response.close_calls, 1)

        owner = {
            "folders": [
                {
                    "id": 1,
                    "attachments": [
                        {
                            "id": 1,
                            "filename": "file.pdf",
                            "download_url": "https://user:secret@indico.esa.int/file.pdf",
                        }
                    ],
                }
            ]
        }
        unsafe_attachment = next(iter(harvester.iter_materials(owner, "event", "1", None)))
        self.assertNotIn("secret", unsafe_attachment.key)
        self.assertNotIn("secret", unsafe_attachment.url)
        unsafe_session = FakeSession([])
        with tempfile.TemporaryDirectory() as temporary:
            unsafe_result = harvester.download_attachment(
                unsafe_session,
                unsafe_attachment,
                Path(temporary) / "file.pdf",
                1,
                0,
                0,
            )
        self.assertEqual(unsafe_result["status"], "inaccessible_non_public_origin")
        self.assertEqual(unsafe_session.calls, [])


class ESAHarvesterMainTests(unittest.TestCase):
    def run_synthetic_harvest(
        self,
        returned_event_id: str,
        *,
        start_date: str = "2020-01-01",
    ) -> tuple[int, dict[str, object], list[object], dict[str, bool]]:
        class MainSession:
            def __init__(self) -> None:
                self.cookies = requests.cookies.RequestsCookieJar()
                self.headers: dict[str, str] = {}
                self.auth: object | None = None
                self.calls: list[str] = []
                self.closed = False
                self.attachment_url = "https://indico.esa.int/file.txt?download=1"

            def get(self, url: str, **_: object) -> FakeResponse:
                self.calls.append(url)
                root_event = {"id": "1", "startDate": start_date}
                if url == harvester.ROOT_URL:
                    payload = {"count": 1, "results": [root_event]}
                elif url == harvester.CATEGORY_URL.format(category_id=5):
                    payload = {"count": 1, "results": [root_event]}
                elif url in {
                    harvester.CATEGORY_URL.format(category_id=6),
                    harvester.CATEGORY_URL.format(category_id=7),
                    harvester.CATEGORY_URL.format(category_id=9),
                }:
                    payload = {"count": 0, "results": []}
                elif url == harvester.EVENT_URL.format(event_id="1"):
                    payload = {
                        "results": [
                            {
                                "id": returned_event_id,
                                "folders": [
                                    {
                                        "id": 3,
                                        "attachments": [
                                            {
                                                "id": 4,
                                                "filename": "file.txt",
                                                "content_type": "text/plain",
                                                "download_url": self.attachment_url,
                                            }
                                        ],
                                    }
                                ],
                                "contributions": [{"db_id": 2, "id": "opaque-contribution"}],
                            }
                        ]
                    }
                elif url == self.attachment_url:
                    return FakeResponse(
                        200,
                        content=b"synthetic attachment text",
                        headers={"Content-Type": "text/plain"},
                        url=url,
                    )
                else:  # pragma: no cover - unexpected requests must fail closed
                    raise AssertionError(url)
                return FakeResponse(
                    200,
                    payload=payload,
                    content=json.dumps(payload).encode("utf-8"),
                    url=url,
                )

            def close(self) -> None:
                self.closed = True

        sessions: list[MainSession] = []
        original_session = harvester.requests.Session

        def session_factory() -> MainSession:
            session = MainSession()
            sessions.append(session)
            return session

        harvester.requests.Session = session_factory  # type: ignore[assignment]
        try:
            with tempfile.TemporaryDirectory() as temporary:
                searches = Path(__file__).resolve().parents[1]
                output_dir = Path(temporary) / "output"
                with contextlib.redirect_stdout(io.StringIO()):
                    exit_code = harvester.main(
                        [
                            "--dictionary",
                            str(searches / "search-concept-dictionary.json"),
                            "--fixtures",
                            str(searches / "fixtures/esa-matcher-regression.json"),
                            "--output-dir",
                            str(output_dir),
                            "--date-end",
                            "2020-01-02",
                            "--event-id",
                            "1",
                            "--event-workers",
                            "1",
                            "--attachment-workers",
                            "1",
                            "--retries",
                            "0",
                        ]
                    )
                summary = json.loads((output_dir / "dry-run-summary.json").read_text())
                files = {
                    "event_raw": (output_dir / "raw" / "events" / "1.json").exists(),
                    "match_results": (output_dir / "match-results.json").exists(),
                    "inventory": (output_dir / "material-inventory.json").exists(),
                }
        finally:
            harvester.requests.Session = original_session  # type: ignore[assignment]
        return exit_code, summary, sessions, files

    def test_main_closes_owned_sessions_after_a_bounded_pilot(self) -> None:
        exit_code, summary, sessions, files = self.run_synthetic_harvest("1")
        self.assertEqual(exit_code, 0)
        self.assertEqual(summary["status"], "success")
        self.assertTrue(summary["source_data_mergeable"])
        self.assertEqual(summary["contribution_exports_retrieved"], 1)
        self.assertEqual(len(sessions), 3)
        self.assertTrue(all(session.closed for session in sessions))
        self.assertTrue(all(files.values()))

    def test_event_identity_failure_is_fail_closed_without_a_mergeable_prefix(self) -> None:
        exit_code, summary, sessions, files = self.run_synthetic_harvest("2")
        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["status"], "failed_source_coverage")
        self.assertFalse(summary["source_data_mergeable"])
        self.assertEqual(summary["contribution_exports_failed"], 1)
        self.assertEqual(summary["partial_event_exports_discarded"], 0)
        self.assertFalse(any(files.values()))
        self.assertTrue(all(session.closed for session in sessions))

    def test_missing_event_date_is_fail_closed_without_event_or_match_artifacts(self) -> None:
        exit_code, summary, sessions, files = self.run_synthetic_harvest(
            "1", start_date="not-a-date"
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["status"], "failed_source_coverage")
        self.assertFalse(summary["source_data_mergeable"])
        self.assertEqual(summary["events_missing_or_unparseable_date"], 1)
        self.assertEqual(summary["contribution_exports_attempted"], 0)
        self.assertFalse(any(files.values()))
        self.assertTrue(all(session.closed for session in sessions))


class ESAHarvesterIdentityTests(unittest.TestCase):
    def test_category_contract_rejects_bad_count_ids_duplicates_and_pagination(self) -> None:
        valid = {"count": 1, "results": [{"id": "1"}]}
        self.assertEqual(harvester.complete_category(valid, "root")[1], ["1"])
        for payload in (
            {"count": True, "results": [{"id": "1"}]},
            {"count": 2, "results": [{"id": "1"}]},
            {"count": 2, "results": [{"id": "1"}, {"id": "1"}]},
            {"count": 1, "results": [{"id": None}]},
            {"count": 1, "results": [{"id": "../1"}]},
            {"count": 1, "pagenav": {"next": 2}, "results": [{"id": "1"}]},
            {"count": 1, "pagenav": "unexpected", "results": [{"id": "1"}]},
        ):
            with self.assertRaises(harvester.HarvestError):
                harvester.complete_category(payload, "root")

    def test_event_and_contribution_ids_are_numeric_and_db_id_is_preferred(self) -> None:
        self.assertEqual(harvester.source_id("007", "event"), "007")
        self.assertEqual(
            harvester.contribution_id({"db_id": 17, "id": "contribution-code"}), "17"
        )
        self.assertEqual(harvester.contribution_id({"id": "18"}), "18")
        for value in (None, True, "", "../1", "event-1", "1.0"):
            with self.assertRaises(harvester.HarvestError):
                harvester.source_id(value, "event")
        for contribution in ({"db_id": "", "id": "17"}, {"db_id": None, "id": "17"}):
            with self.assertRaises(harvester.HarvestError):
                harvester.contribution_id(contribution)

    def test_bounded_selector_is_pilot_only_small_and_exact(self) -> None:
        self.assertEqual(
            harvester.bounded_event_ids(["1", "2"], "pilot_not_candidate_search"),
            {"1", "2"},
        )
        for values, classification in (
            (["1"], "final_run"),
            (["1", "1"], "pilot_not_candidate_search"),
            ([str(number) for number in range(6)], "pilot_not_candidate_search"),
            (["not-an-id"], "pilot_not_candidate_search"),
            ([""], "pilot_not_candidate_search"),
        ):
            with self.assertRaises(harvester.HarvestError):
                harvester.bounded_event_ids(values, classification)


if __name__ == "__main__":
    unittest.main()
