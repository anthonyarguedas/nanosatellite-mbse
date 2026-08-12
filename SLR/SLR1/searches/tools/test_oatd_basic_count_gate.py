#!/usr/bin/env python3
"""Offline synthetic regressions for the OATD aggregate-only gate."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import nullcontext, redirect_stdout
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlsplit

SCRIPT_PATH = Path(__file__).with_name("oatd_basic_count_gate.py")
SPEC = importlib.util.spec_from_file_location("oatd_basic_count_gate", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not import {SCRIPT_PATH}")
oatd = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = oatd
SPEC.loader.exec_module(oatd)


def valid_payload(*, total: int = 43) -> dict[str, object]:
    end = min(total, 30)
    blank_select = {"count": 1, "value": ""}
    blank_input = {"count": 1, "value": ""}
    return {
        "host": "oatd.org",
        "path": "/oatd/search",
        "protocol": "https:",
        "urlQueryExact": True,
        "urlFormExact": True,
        "urlParameterNames": ["form", "q"],
        "reportCount": 1,
        "queryEchoExact": True,
        "rangeParsed": True,
        "rangeStart": 1,
        "rangeEnd": end,
        "total": total,
        "rowCount": end,
        "sort": {"count": 1, "value": "relevanace"},
        "pageSize": {"count": 1, "value": "30"},
        "language": dict(blank_select),
        "country": dict(blank_select),
        "earliest": dict(blank_input),
        "latest": dict(blank_input),
        "ccCount": 1,
        "ccChecked": False,
        "challenge": False,
        "busy": False,
        "syntaxError": False,
        "ready": True,
    }


class FrozenRegistryTests(unittest.TestCase):
    def test_registry_is_exact_finite_and_plan_synchronized(self) -> None:
        entries = oatd.load_frozen_queries()
        self.assertEqual(tuple(entries), oatd.QUERY_IDS)
        plan_path = oatd.QUERY_MANIFEST_PATH.parents[1] / "query-search-plan.md"
        plan = plan_path.read_text(encoding="utf-8")
        for query_id, entry in entries.items():
            match = re.search(
                rf"^### {re.escape(query_id)}(?:\s+[^\n]*)?\n\n```text\n(.*?)\n```",
                plan,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, query_id)
            self.assertEqual(entry["query"], match.group(1).strip())
            self.assertNotIn("*", entry["query"])
            self.assertNotIn("?", entry["query"])

    def test_pinned_manifest_tamper_fails(self) -> None:
        original = oatd.QUERY_MANIFEST_SHA256
        try:
            oatd.QUERY_MANIFEST_SHA256 = "0" * 64
            with self.assertRaises(oatd.InputGateError):
                oatd.load_frozen_queries()
        finally:
            oatd.QUERY_MANIFEST_SHA256 = original

    def test_manifest_is_hashed_and_decoded_from_one_read(self) -> None:
        manifest_bytes = oatd.QUERY_MANIFEST_PATH.read_bytes()
        read_once_path = mock.Mock()
        read_once_path.read_bytes.return_value = manifest_bytes
        read_once_path.read_text.side_effect = AssertionError("manifest must not be reread")
        real_sha256 = hashlib.sha256
        real_loads = json.loads
        with (
            mock.patch.object(oatd, "QUERY_MANIFEST_PATH", read_once_path),
            mock.patch.object(oatd.hashlib, "sha256", wraps=real_sha256) as sha256_mock,
            mock.patch.object(oatd.json, "loads", wraps=real_loads) as loads_mock,
        ):
            entries = oatd.load_frozen_queries()
        self.assertEqual(tuple(entries), oatd.QUERY_IDS)
        read_once_path.read_bytes.assert_called_once_with()
        read_once_path.read_text.assert_not_called()
        self.assertIs(sha256_mock.call_args_list[0].args[0], manifest_bytes)
        loads_mock.assert_called_once_with(manifest_bytes)
        self.assertIs(loads_mock.call_args.args[0], manifest_bytes)

    def test_manifest_read_decode_and_type_failures_are_fixed(self) -> None:
        cases: tuple[tuple[object, str], ...] = (
            (OSError("raw read failure"), oatd.QUERY_MANIFEST_SHA256),
            (b"{", hashlib.sha256(b"{").hexdigest()),
            (object(), oatd.QUERY_MANIFEST_SHA256),
        )
        for response, expected_sha256 in cases:
            manifest_path = mock.Mock()
            if isinstance(response, BaseException):
                manifest_path.read_bytes.side_effect = response
            else:
                manifest_path.read_bytes.return_value = response
            with (
                mock.patch.object(oatd, "QUERY_MANIFEST_PATH", manifest_path),
                mock.patch.object(oatd, "QUERY_MANIFEST_SHA256", expected_sha256),
                self.assertRaises(oatd.InputGateError) as raised,
            ):
                oatd.load_frozen_queries()
            self.assertEqual(str(raised.exception), "The pinned thesis-source query manifest is unreadable.")
            self.assertNotIn("raw read failure", str(raised.exception))

    def test_url_contains_only_exact_basic_query_parameters(self) -> None:
        query = oatd.load_frozen_queries()["OATD-B2"]["query"]
        parsed = urlsplit(oatd.build_search_url(query))
        self.assertEqual((parsed.scheme, parsed.netloc, parsed.path), ("https", "oatd.org", "/oatd/search"))
        self.assertEqual(parse_qs(parsed.query), {"q": [query], "form": ["basic"]})

    def test_nonloopback_or_sensitive_cdp_urls_fail(self) -> None:
        for value in (
            "http://192.168.1.2:9222",
            "http://user:pass@localhost:9222",
            "http://localhost:9222?token=secret",
        ):
            with self.assertRaises(oatd.InputGateError):
                oatd.validate_local_cdp_url(value)
        self.assertEqual(oatd.validate_local_cdp_url("http://127.0.0.1:9222/"), "http://127.0.0.1:9222")


class AggregateStateTests(unittest.TestCase):
    def test_first_page_and_terminal_ranges_reconcile(self) -> None:
        first = oatd.parse_count_state(valid_payload(total=43))
        self.assertEqual(first["source_total"], 43)
        self.assertEqual(first["displayed_range_end"], 30)
        self.assertEqual(first["result_container_count"], 30)
        terminal = oatd.parse_count_state(valid_payload(total=23))
        self.assertEqual(terminal["displayed_range_end"], 23)
        self.assertEqual(terminal["result_container_count"], 23)

    def test_native_zero_is_deliberately_not_accepted(self) -> None:
        payload = valid_payload(total=1)
        payload.update({"rangeEnd": 0, "total": 0, "rowCount": 0})
        with self.assertRaisesRegex(oatd.ProtocolGateError, "native_zero"):
            oatd.parse_count_state(payload)

    def test_busy_challenge_and_syntax_are_not_zero(self) -> None:
        for field, error_type in (
            ("busy", oatd.AccessGateError),
            ("challenge", oatd.AccessGateError),
            ("syntaxError", oatd.ProtocolGateError),
        ):
            payload = valid_payload()
            payload[field] = True
            with self.assertRaises(error_type):
                oatd.parse_count_state(payload)

    def test_rewrite_missing_total_and_short_rows_fail(self) -> None:
        cases = []
        rewritten = valid_payload()
        rewritten["urlQueryExact"] = False
        cases.append(rewritten)
        missing = valid_payload()
        missing["rangeParsed"] = False
        missing["total"] = None
        cases.append(missing)
        short = valid_payload()
        short["rowCount"] = 29
        cases.append(short)
        extra_parameter = valid_payload()
        extra_parameter["urlParameterNames"] = ["form", "page", "q"]
        cases.append(extra_parameter)
        for payload in cases:
            with self.assertRaises(oatd.ProtocolGateError):
                oatd.parse_count_state(payload)

    def test_sort_page_size_and_filter_drift_fail(self) -> None:
        mutations = (
            ("sort", {"count": 1, "value": "date"}),
            ("pageSize", {"count": 1, "value": "100"}),
            ("language", {"count": 1, "value": "English"}),
            ("country", {"count": 0, "value": ""}),
            ("earliest", {"count": 1, "value": "2011"}),
            ("latest", {"count": 1, "value": "2026"}),
        )
        for key, value in mutations:
            payload = valid_payload()
            payload[key] = value
            with self.assertRaises(oatd.ProtocolGateError, msg=key):
                oatd.parse_count_state(payload)
        cc = valid_payload()
        cc["ccChecked"] = True
        with self.assertRaises(oatd.ProtocolGateError):
            oatd.parse_count_state(cc)

    def test_invalid_types_fail_closed(self) -> None:
        for key, value in (("ready", 1), ("total", True), ("rowCount", "30")):
            payload = valid_payload()
            payload[key] = value
            with self.assertRaises(oatd.ProtocolGateError):
                oatd.parse_count_state(payload)


class PrivacyAndArtifactTests(unittest.TestCase):
    def test_state_script_has_no_card_content_or_browser_storage_access(self) -> None:
        script = oatd.OATD_COUNT_STATE_SCRIPT
        for forbidden in (
            "outerHTML", "innerHTML", "document.body", "localStorage", "sessionStorage",
            "document.cookie", "querySelectorAll(\"a", ".result a", "href:", "recordId",
        ):
            self.assertNotIn(forbidden, script)
        self.assertNotIn("h1", script)
        self.assertNotIn("h2", script)
        self.assertIn("document.title", script)
        self.assertIn(".error, .error_message, [role='alert']", script)
        self.assertIn('element.matches(".result")', script)

    def test_success_artifact_is_noncandidate_and_allowlisted(self) -> None:
        state = oatd.parse_count_state(valid_payload(total=23))
        artifact = oatd.success_artifact(
            "OATD-B1", "1" * 64, state,
            started_at="2026-08-11T00:00:00.000Z",
            completed_at="2026-08-11T00:00:01.000Z",
        )
        oatd.validate_artifact_allowlist(artifact)
        self.assertFalse(artifact["merge_input"])
        self.assertFalse(artifact["candidate_import_allowed"])
        self.assertEqual(artifact["candidate_records_serialized"], 0)
        self.assertNotIn("results", artifact)

    def test_failure_artifact_uses_null_and_fixed_code(self) -> None:
        artifact = oatd.failure_artifact(
            "OATD-B2", "2" * 64, oatd.TimeoutGateError("secret raw message"),
            started_at=None, completed_at="2026-08-11T00:00:01.000Z",
        )
        oatd.validate_artifact_allowlist(artifact)
        self.assertIsNone(artifact["source_total"])
        self.assertEqual(artifact["failure_code"], "timeout")
        self.assertNotIn("secret raw message", json.dumps(artifact))

    def test_injected_candidate_or_sensitive_fields_are_rejected(self) -> None:
        for key in ("title", "author", "abstract", "snippet", "recordId", "url", "results", "token"):
            artifact = {"artifact_kind": "test", key: "injected"}
            with self.assertRaises(oatd.ProtocolGateError, msg=key):
                oatd.validate_artifact_allowlist(artifact)

    def test_atomic_output_is_owner_only_and_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gate.json"
            with (
                mock.patch.object(oatd.os, "link", wraps=oatd.os.link) as link_mock,
                mock.patch.object(
                    oatd.os,
                    "replace",
                    side_effect=AssertionError("publication must not replace an artifact"),
                ) as replace_mock,
            ):
                oatd.atomic_write_json(path, {"status": "synthetic"})
                original = path.read_bytes()
                with self.assertRaises(oatd.InputGateError):
                    oatd.atomic_write_json(path, {"status": "replacement"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(link_mock.call_count, 2)
            replace_mock.assert_not_called()


class MainFailureMappingTests(unittest.TestCase):
    def test_runtime_error_writes_a_fixed_failure_artifact_without_a_browser(self) -> None:
        calls: list[None] = []

        async def synthetic_browser_failure(*_args: object, **_kwargs: object) -> dict[str, object]:
            calls.append(None)
            raise RuntimeError("synthetic raw browser failure")

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "gate.json"
            captured_stdout = io.StringIO()
            with (
                mock.patch.object(oatd, "exclusive_source_lock", return_value=nullcontext()),
                mock.patch.object(oatd, "run_browser_gate", new=synthetic_browser_failure),
                redirect_stdout(captured_stdout),
            ):
                exit_code = oatd.main([
                    "--query-id", "OATD-B2",
                    "--output-path", str(output_path),
                    "--cdp-url", "http://127.0.0.1:9222",
                ])
            artifact = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 1)
        self.assertEqual(calls, [None])
        self.assertEqual(artifact["status"], "error")
        self.assertEqual(artifact["failure_code"], "other_fail_closed")
        self.assertIsNone(artifact["source_total"])
        self.assertNotIn("synthetic raw browser failure", json.dumps(artifact))
        self.assertNotIn("synthetic raw browser failure", captured_stdout.getvalue())
        self.assertIn("other_fail_closed", captured_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
