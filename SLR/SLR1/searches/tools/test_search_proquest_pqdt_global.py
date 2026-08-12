#!/usr/bin/env python3
"""Offline synthetic regressions for the exact-PQDT aggregate-only wrapper."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import types
import unittest
from contextlib import nullcontext, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).with_name("search_proquest_pqdt_global.py")
SPEC = importlib.util.spec_from_file_location("search_proquest_pqdt_global", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not import {SCRIPT_PATH}")
pqdt = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pqdt
SPEC.loader.exec_module(pqdt)


def database_payload() -> dict[str, object]:
    return {
        "protocol": "https:",
        "host": "www.proquest.com",
        "path": "/pqdtglobal/databases/advanced",
        "targetCount": 1,
        "selectedCount": 1,
        "exactTargetOnly": True,
        "selectedTargetLabelAllowed": True,
        "challenge": False,
        "loginRoute": False,
        "ready": True,
    }


def form_payload() -> dict[str, object]:
    return {
        "protocol": "https:",
        "host": "www.proquest.com",
        "path": "/pqdtglobal/commandline",
        "titleHasSource": True,
        "sortCount": 1,
        "sortValue": "relevance",
        "pageSizeCount": 1,
        "pageSizeValue": "20",
        "dedupCount": 1,
        "dedupChecked": False,
        "spellingCount": 1,
        "spellingChecked": True,
        "formsCount": 1,
        "formsChecked": True,
        "queryFieldCount": 1,
        "submitCount": 1,
        "fullTextControlCount": 1,
        "fullTextChecked": False,
        "checkedDiscoveryLimiterCount": 0,
        "challenge": False,
        "loginRoute": False,
        "ready": True,
    }


def count_payload(*, total: str = "17 results") -> dict[str, object]:
    return {
        "protocol": "https:",
        "host": "www.proquest.com",
        "pathStartsProduct": True,
        "titleHasSource": True,
        "queryFieldCount": 1,
        "queryEchoExact": True,
        "totalNodeCount": 1,
        "totalText": total,
        "explicitZero": False,
        "zeroNodeCount": 0,
        "syntaxError": False,
        "challenge": False,
        "loginRoute": False,
        "ready": True,
    }


class FrozenContractTests(unittest.TestCase):
    def test_registry_has_exact_aliases_and_plan_bodies(self) -> None:
        entries = pqdt.load_frozen_queries()
        self.assertEqual(tuple(entries), pqdt.QUERY_IDS)
        plan_path = pqdt.QUERY_MANIFEST_PATH.parents[1] / "query-search-plan.md"
        plan = plan_path.read_text(encoding="utf-8")
        for query_id, entry in entries.items():
            body_id = query_id.replace("PQDT-", "PQ-", 1)
            match = re.search(
                rf"^### {re.escape(body_id)}(?:\s+[^\n]*)?\n\n```text\n(.*?)\n```",
                plan,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, body_id)
            self.assertEqual(entry["query"], match.group(1).strip())
            self.assertEqual(entry["query"].count("YR(2011-2026)"), 1)
            self.assertEqual(entry["query"].count("LA(English)"), 1)

    def test_pinned_manifest_tamper_fails(self) -> None:
        original = pqdt.QUERY_MANIFEST_SHA256
        try:
            pqdt.QUERY_MANIFEST_SHA256 = "f" * 64
            with self.assertRaises(pqdt.InputGateError):
                pqdt.load_frozen_queries()
        finally:
            pqdt.QUERY_MANIFEST_SHA256 = original

    def test_manifest_is_hashed_and_decoded_from_one_read(self) -> None:
        manifest_bytes = pqdt.QUERY_MANIFEST_PATH.read_bytes()
        read_once_path = mock.Mock()
        read_once_path.read_bytes.return_value = manifest_bytes
        read_once_path.read_text.side_effect = AssertionError("manifest must not be reread")
        real_sha256 = hashlib.sha256
        real_loads = json.loads
        with (
            mock.patch.object(pqdt, "QUERY_MANIFEST_PATH", read_once_path),
            mock.patch.object(pqdt.hashlib, "sha256", wraps=real_sha256) as sha256_mock,
            mock.patch.object(pqdt.json, "loads", wraps=real_loads) as loads_mock,
        ):
            entries = pqdt.load_frozen_queries()
        self.assertEqual(tuple(entries), pqdt.QUERY_IDS)
        read_once_path.read_bytes.assert_called_once_with()
        read_once_path.read_text.assert_not_called()
        self.assertIs(sha256_mock.call_args_list[0].args[0], manifest_bytes)
        loads_mock.assert_called_once_with(manifest_bytes)
        self.assertIs(loads_mock.call_args.args[0], manifest_bytes)

    def test_manifest_read_decode_and_type_failures_are_fixed(self) -> None:
        cases: tuple[tuple[object, str], ...] = (
            (OSError("raw read failure"), pqdt.QUERY_MANIFEST_SHA256),
            (b"{", hashlib.sha256(b"{").hexdigest()),
            (object(), pqdt.QUERY_MANIFEST_SHA256),
        )
        for response, expected_sha256 in cases:
            manifest_path = mock.Mock()
            if isinstance(response, BaseException):
                manifest_path.read_bytes.side_effect = response
            else:
                manifest_path.read_bytes.return_value = response
            with (
                mock.patch.object(pqdt, "QUERY_MANIFEST_PATH", manifest_path),
                mock.patch.object(pqdt, "QUERY_MANIFEST_SHA256", expected_sha256),
                self.assertRaises(pqdt.InputGateError) as raised,
            ):
                pqdt.load_frozen_queries()
            self.assertEqual(str(raised.exception), "The pinned thesis-source query manifest is unreadable.")
            self.assertNotIn("raw read failure", str(raised.exception))

    def test_cli_exposes_no_arbitrary_query_or_database(self) -> None:
        parser = pqdt.build_parser()
        destinations = {action.dest for action in parser._actions}
        self.assertNotIn("query", destinations)
        self.assertNotIn("database", destinations)
        self.assertNotIn("source", destinations)
        self.assertNotIn("entry_url", destinations)
        self.assertNotIn("limit", destinations)
        self.assertNotIn("max_pages", destinations)
        self.assertNotIn("language", destinations)
        self.assertNotIn("year_start", destinations)

    def test_nonloopback_or_sensitive_cdp_urls_fail(self) -> None:
        for value in (
            "http://example.com:9222",
            "http://user:pass@localhost:9222",
            "http://localhost:9222?session=secret",
        ):
            with self.assertRaises(pqdt.InputGateError):
                pqdt.validate_local_cdp_url(value)
        self.assertEqual(pqdt.validate_local_cdp_url("http://localhost:9222/"), "http://localhost:9222")


class ExactDatabaseAndControlTests(unittest.TestCase):
    def test_exact_pqdt_only_selection_passes(self) -> None:
        self.assertEqual(pqdt.parse_database_state(database_payload()), {"exact_database_selection": True})

    def test_extra_target_or_selected_source_fails(self) -> None:
        for key, value in (
            ("targetCount", 2),
            ("selectedCount", 2),
            ("exactTargetOnly", False),
            ("selectedTargetLabelAllowed", False),
        ):
            payload = database_payload()
            payload[key] = value
            with self.assertRaises(pqdt.ProtocolGateError, msg=key):
                pqdt.parse_database_state(payload)

    def test_wrong_route_challenge_and_login_fail(self) -> None:
        wrong = database_payload()
        wrong["path"] = "/ataindex/databases/advanced"
        with self.assertRaises(pqdt.ProtocolGateError):
            pqdt.parse_database_state(wrong)
        for key in ("challenge", "loginRoute"):
            payload = database_payload()
            payload[key] = True
            with self.assertRaises(pqdt.AccessGateError):
                pqdt.parse_database_state(payload)

    def test_frozen_form_controls_pass(self) -> None:
        observed = pqdt.parse_form_state(form_payload())
        self.assertEqual(observed["sort"], "Relevance")
        self.assertEqual(observed["page_size"], 20)
        self.assertTrue(observed["spelling_variants"])
        self.assertTrue(observed["plural_and_adjective_variants"])
        self.assertTrue(observed["full_text_control_visible"])
        self.assertFalse(observed["full_text_limiter"])
        self.assertNotIn("other_discovery_limiters", observed)

    def test_absent_or_ambiguous_full_text_control_fails(self) -> None:
        for count in (0, 2):
            payload = form_payload()
            payload["fullTextControlCount"] = count
            payload["fullTextChecked"] = False
            with self.assertRaisesRegex(pqdt.ProtocolGateError, "full_text_control"):
                pqdt.parse_form_state(payload)

    def test_scope_is_reasserted_on_the_single_owned_page(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertEqual(source.count("await assert_exact_pqdt_only_selection(page, timeout_seconds)"), 2)
        self.assertIn('"database_selection_assertion_count": selection_assertion_count', source)
        self.assertEqual(source.count("context.new_page()"), 1)
        self.assertNotRegex(source, r"\b(?:browser|context)\.close\(")

    def test_scope_assertion_sequence_returns_two_on_one_page(self) -> None:
        selection_pages: list[object] = []
        navigations: list[str] = []
        configured_pages: list[object] = []

        class FakeLocator:
            def __init__(self) -> None:
                self.fills: list[str] = []
                self.clicks = 0

            async def count(self) -> int:
                return 1

            async def fill(self, value: str) -> None:
                self.fills.append(value)

            async def click(self) -> None:
                self.clicks += 1

        class FakePage:
            def __init__(self) -> None:
                self.field = FakeLocator()
                self.button = FakeLocator()
                self.close_count = 0

            def locator(self, selector: str) -> FakeLocator:
                if selector == "#searchTerm:visible":
                    return self.field
                if selector == "#submit_7:visible":
                    return self.button
                raise AssertionError(f"unexpected locator {selector}")

            async def close(self) -> None:
                self.close_count += 1

        class FakeContext:
            def __init__(self, page: FakePage) -> None:
                self.page = page
                self.new_page_count = 0

            def set_default_timeout(self, _timeout: int) -> None:
                pass

            def set_default_navigation_timeout(self, _timeout: int) -> None:
                pass

            async def new_page(self) -> FakePage:
                self.new_page_count += 1
                return self.page

        class FakeChromium:
            def __init__(self, context: FakeContext) -> None:
                self.context = context

            async def connect_over_cdp(self, _url: str, *, timeout: int) -> object:
                if timeout <= 0:
                    raise AssertionError("timeout must be positive")
                return types.SimpleNamespace(contexts=[self.context])

        class FakePlaywrightManager:
            def __init__(self, chromium: FakeChromium) -> None:
                self.playwright = types.SimpleNamespace(chromium=chromium)

            async def __aenter__(self) -> object:
                return self.playwright

            async def __aexit__(self, *_args: object) -> bool:
                return False

        page = FakePage()
        context = FakeContext(page)
        chromium = FakeChromium(context)
        async_api = types.ModuleType("playwright.async_api")
        async_api.async_playwright = lambda: FakePlaywrightManager(chromium)
        playwright_package = types.ModuleType("playwright")
        playwright_package.__path__ = []
        playwright_package.async_api = async_api

        async def fake_navigate(page_arg: object, url: str, _timeout: float) -> None:
            self.assertIs(page_arg, page)
            navigations.append(url)

        async def fake_selection(page_arg: object, _timeout: float) -> None:
            self.assertIs(page_arg, page)
            selection_pages.append(page_arg)

        async def fake_configure(page_arg: object) -> None:
            self.assertIs(page_arg, page)
            configured_pages.append(page_arg)

        async def fake_wait_payload(
            page_arg: object, script: str, _argument: object, _timeout: float,
        ) -> dict[str, object]:
            self.assertIs(page_arg, page)
            if script == pqdt.PQDT_FORM_STATE_SCRIPT:
                return form_payload()
            if script == pqdt.PQDT_COUNT_STATE_SCRIPT:
                return count_payload()
            raise AssertionError("unexpected state script")

        with (
            mock.patch.dict(sys.modules, {"playwright": playwright_package, "playwright.async_api": async_api}),
            mock.patch.object(pqdt, "navigate", new=fake_navigate),
            mock.patch.object(pqdt, "assert_exact_pqdt_only_selection", new=fake_selection),
            mock.patch.object(pqdt, "configure_result_options", new=fake_configure),
            mock.patch.object(pqdt, "wait_payload", new=fake_wait_payload),
        ):
            total, observed = asyncio.run(
                pqdt.run_browser_gate("frozen query", cdp_url="http://127.0.0.1:9222", timeout_seconds=1)
            )

        self.assertEqual(total, 17)
        self.assertEqual(observed["database_selection_assertion_count"], 2)
        self.assertEqual(navigations, [pqdt.DATABASE_SELECTION_URL, pqdt.DATABASE_SELECTION_URL, pqdt.COMMAND_LINE_URL])
        self.assertEqual(selection_pages, [page, page])
        self.assertEqual(configured_pages, [page])
        self.assertEqual(context.new_page_count, 1)
        self.assertEqual(page.field.fills, ["frozen query"])
        self.assertEqual(page.button.clicks, 1)
        self.assertEqual(page.close_count, 1)

    def test_sort_page_dedup_variant_or_limiter_drift_fails(self) -> None:
        mutations = (
            ("sortValue", "date"),
            ("pageSizeValue", "100"),
            ("dedupChecked", True),
            ("spellingChecked", False),
            ("formsChecked", False),
            ("fullTextChecked", True),
            ("checkedDiscoveryLimiterCount", 1),
            ("queryFieldCount", 2),
        )
        for key, value in mutations:
            payload = form_payload()
            payload[key] = value
            with self.assertRaises(pqdt.ProtocolGateError, msg=key):
                pqdt.parse_form_state(payload)


class AggregateStateTests(unittest.TestCase):
    def test_positive_comma_total_passes(self) -> None:
        self.assertEqual(pqdt.parse_count_state(count_payload(total="1,234 results")), 1234)

    def test_native_zero_is_deliberately_unvalidated(self) -> None:
        payload = count_payload(total="")
        payload.update({"totalNodeCount": 0, "explicitZero": True, "zeroNodeCount": 1})
        with self.assertRaisesRegex(pqdt.ProtocolGateError, "native_zero"):
            pqdt.parse_count_state(payload)

    def test_syntax_challenge_login_and_echo_failure_are_not_zero(self) -> None:
        for key, error_type in (
            ("syntaxError", pqdt.ProtocolGateError),
            ("challenge", pqdt.AccessGateError),
            ("loginRoute", pqdt.AccessGateError),
            ("queryEchoExact", pqdt.ProtocolGateError),
        ):
            payload = count_payload()
            payload[key] = key != "queryEchoExact"
            with self.assertRaises(error_type, msg=key):
                pqdt.parse_count_state(payload)

    def test_missing_ambiguous_or_unrecognized_total_fails(self) -> None:
        for key, value in (("totalNodeCount", 0), ("totalNodeCount", 2), ("totalText", "about 17")):
            payload = count_payload()
            payload[key] = value
            with self.assertRaises(pqdt.ProtocolGateError):
                pqdt.parse_count_state(payload)

    def test_wrong_product_route_or_title_fails(self) -> None:
        for key in ("pathStartsProduct", "titleHasSource"):
            payload = count_payload()
            payload[key] = False
            with self.assertRaises(pqdt.ProtocolGateError):
                pqdt.parse_count_state(payload)


class PrivacyAndOutputTests(unittest.TestCase):
    def test_count_scripts_do_not_read_result_cards_ids_or_storage(self) -> None:
        combined = (
            f"{pqdt.PQDT_DATABASE_STATE_SCRIPT}\n"
            f"{pqdt.PQDT_FORM_STATE_SCRIPT}\n"
            f"{pqdt.PQDT_COUNT_STATE_SCRIPT}"
        )
        for forbidden in (
            "#lor_container", "citationDocTitleLink_", ".previewTitle", ".snippet",
            ".scholUnivAuthors", "paperId", "recordId", "outerHTML", "innerHTML",
            "document.body", "document.cookie", "localStorage", "sessionStorage",
        ):
            self.assertNotIn(forbidden, combined)

    def test_success_artifact_is_fixed_noncandidate_output(self) -> None:
        artifact = pqdt.make_artifact(
            "PQDT-B1", "1" * 64,
            started_at="2026-08-11T00:00:00.000Z",
            completed_at="2026-08-11T00:00:01.000Z",
            total=17,
            observed={"exact_database_selection": True},
        )
        pqdt.validate_artifact_allowlist(artifact)
        self.assertFalse(artifact["merge_input"])
        self.assertFalse(artifact["candidate_import_allowed"])
        self.assertEqual(artifact["candidate_records_serialized"], 0)
        self.assertNotIn("results", artifact)
        self.assertIn(
            "PQDT-02: absent/hidden/type/degree/access limiter proof remains live",
            artifact["unvalidated"],
        )
        self.assertIn(
            "PQDT-02: cooperative lock cannot eliminate external ABA",
            artifact["unvalidated"],
        )

    def test_failure_artifact_is_null_and_does_not_serialize_raw_error(self) -> None:
        artifact = pqdt.make_artifact(
            "PQDT-B2", "2" * 64,
            started_at=None,
            completed_at="2026-08-11T00:00:01.000Z",
            total=17,
            error=pqdt.TimeoutGateError("https://www.proquest.com/pqdtglobal/results/SECRET/1?token=x"),
        )
        pqdt.validate_artifact_allowlist(artifact)
        self.assertIsNone(artifact["source_total"])
        self.assertEqual(artifact["failure_code"], "timeout")
        self.assertNotIn("SECRET", json.dumps(artifact))

    def test_injected_candidate_or_secret_fields_are_rejected(self) -> None:
        for key in ("title", "author", "abstract", "snippet", "paperId", "recordId", "url", "results", "rank", "token"):
            with self.assertRaises(pqdt.ProtocolGateError, msg=key):
                pqdt.validate_artifact_allowlist({"artifact_kind": "test", key: "injected"})

    def test_atomic_output_is_owner_only_and_immutable(self) -> None:
        self.assertNotIn("os.replace", SCRIPT_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gate.json"
            with (
                mock.patch.object(pqdt.os, "link", wraps=pqdt.os.link) as link_mock,
                mock.patch.object(
                    pqdt.os,
                    "replace",
                    side_effect=AssertionError("publication must not replace an artifact"),
                ) as replace_mock,
            ):
                pqdt.atomic_write_json(path, {"status": "synthetic"})
                original = path.read_bytes()
                with self.assertRaises(pqdt.InputGateError):
                    pqdt.atomic_write_json(path, {"status": "replacement"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(link_mock.call_count, 2)
            replace_mock.assert_not_called()


class MainFailureMappingTests(unittest.TestCase):
    def test_runtime_error_writes_a_fixed_failure_artifact_without_a_browser(self) -> None:
        calls: list[None] = []

        async def synthetic_browser_failure(*_args: object, **_kwargs: object) -> tuple[int, dict[str, object]]:
            calls.append(None)
            raise RuntimeError("synthetic raw browser failure")

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "gate.json"
            captured_stdout = io.StringIO()
            with (
                mock.patch.object(pqdt, "exclusive_source_lock", return_value=nullcontext()),
                mock.patch.object(pqdt, "run_browser_gate", new=synthetic_browser_failure),
                redirect_stdout(captured_stdout),
            ):
                exit_code = pqdt.main([
                    "--query-id", "PQDT-B2",
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
