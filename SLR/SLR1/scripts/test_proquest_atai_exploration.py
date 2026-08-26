"""Focused source-free tests for the bounded ATAI X exploration runner."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPTS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "test_slr1_proquest_atai_exploration",
    SCRIPTS / "proquest_atai_exploration.py",
)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("could not load ATAI exploration runner")
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class FakeLocator:
    def __init__(self, *, value: str = "", enabled: bool = True, click=None):
        self.value = value
        self.enabled = enabled
        self.click_callback = click
        self.first = self

    async def count(self) -> int:
        return 1

    async def is_visible(self) -> bool:
        return True

    async def is_enabled(self) -> bool:
        return self.enabled

    async def fill(self, value: str) -> None:
        self.value = value

    async def input_value(self) -> str:
        return self.value

    async def click(self) -> None:
        if self.click_callback is not None:
            self.click_callback()


class FakePage:
    def __init__(self, context, *, url: str, target_id: str):
        self.context = context
        self.url = url
        self.target_id = target_id
        self.closed = False
        self.native_clicks = 0
        self.query_field = FakeLocator()
        self.database_submit_button = FakeLocator()
        self.submit_button = FakeLocator(click=self._submit_query)

    def is_closed(self) -> bool:
        return self.closed

    async def close(self) -> None:
        self.closed = True
        self.context.pages = [page for page in self.context.pages if page is not self]

    def _submit_query(self) -> None:
        self.native_clicks += 1
        self.url = "https://www.proquest.com/ataindex/results/frozen/1"

    def locator(self, selector: str) -> FakeLocator:
        if selector == "#searchTerm":
            return self.query_field
        if selector == "#submit_7":
            return self.submit_button
        if selector == "#submit_2:visible, #submit_4:visible":
            return self.database_submit_button
        if selector.endswith(":visible") and selector.startswith("#dbcb_"):
            return FakeLocator()
        raise AssertionError(f"unexpected fake selector: {selector}")

    async def evaluate(self, script, payload=None):
        if script == "options":
            return {
                "host": "www.proquest.com",
                "blocked": False,
                "requiresAccess": False,
                "resultOptions": {},
                "limiterState": {},
            }
        if script == runner.SENTINEL_RESULT_STATE_SCRIPT:
            return {
                "protocol": "https:",
                "host": "www.proquest.com",
                "titleExact": True,
                "productLinkExact": True,
                "queryFieldCount": 1,
                "queryMatches": payload["query"] == runner.FIXED_COMMAND_QUERY,
                "resultRoute": True,
                "routeClean": True,
                "pageOrdinal": 1,
                "totalNodeCount": 1,
                "totalText": "3 results",
                "zeroResults": False,
                "rowCount": 3,
                "syntaxError": False,
                "blocked": False,
                "requiresAccess": False,
                "ready": True,
            }
        raise AssertionError("unexpected fake page evaluation")


class FakeContext:
    def __init__(self):
        self.pages = []
        self.anchor = FakePage(
            self,
            url="https://www.proquest.com/ataindex/commandline",
            target_id="anchor-target",
        )
        self.pages.append(self.anchor)

    async def new_page(self):
        page = FakePage(self, url="about:blank", target_id="owned-target")
        self.pages.append(page)
        return page


class FakeBrowser:
    def __init__(self, context):
        self.contexts = [context]


class FakeConnection:
    def __init__(self, browser, context):
        self.browser = browser
        self.context = context
        self.owns_browser = False
        self.attached_cdp = True


class FakeCommon:
    def __init__(self):
        self.context = FakeContext()
        self.browser = FakeBrowser(self.context)

    async def open_chrome_connection(self, playwright, **kwargs):
        self.open_kwargs = kwargs
        return FakeConnection(self.browser, self.context)

    async def new_owned_chrome_page(self, context, **kwargs):
        self.new_page_kwargs = kwargs
        return await context.new_page()

    async def _target_id_for_page(self, page):
        return page.target_id

    async def close_owned_chrome_page_only_verified(self, page):
        await page.close()
        return SimpleNamespace(verified=True)


class FakeAdapter:
    SOURCE_NAME = runner.SOURCE_LABEL
    ENTRY_SITE = runner.ENTRY_SITE
    SOURCE_SITE = runner.SOURCE_SITE
    TARGET_DATABASE_LABEL = runner.TARGET_DATABASE_LABEL
    DATABASE_SELECTION_URL = runner.DATABASE_SELECTION_URL
    COMMAND_LINE_URL = runner.COMMAND_LINE_URL
    RESULT_OPTIONS_STATE_SCRIPT = "options"

    def __init__(self):
        self._common = FakeCommon()
        self.selected = {
            runner.TARGET_DATABASE_LABEL: False,
            "Unrelated database": True,
            "Another database": False,
        }
        self.selection_submits = 0

    async def navigate(self, page, url, timeout):
        page.url = url

    async def wait_for_database_selection_route(self, page, **kwargs):
        if not page.url.endswith(runner.DATABASE_SELECTION_ROUTE):
            raise AssertionError("fake database route was not used")

    async def dismiss_ephemeral_cookie_dialog(self, page, **kwargs):
        return None

    async def ensure_aerospace_hierarchy_expanded(self, page, **kwargs):
        return None

    async def read_database_options(self, page, **kwargs):
        return [
            SimpleNamespace(label=label, checked=checked, element_id=f"dbcb_{label}")
            for label, checked in self.selected.items()
        ]

    async def set_database_selection(self, page, desired, **kwargs):
        self.selected = {
            label: label in desired for label in self.selected
        }

    async def submit_database_selection(self, page, *args, **kwargs):
        self.selection_submits += 1
        page.url = "https://www.proquest.com/ataindex/"

    async def wait_for_exact_index_route(self, page, **kwargs):
        return None

    async def configure_result_options(self, page, **kwargs):
        return None

    def result_option_snapshot_from_payload(self, payload):
        return SimpleNamespace(is_frozen=True, controls=(1, 2, 3, 4, 5, 6))

    def limiter_evidence_from_payload(self, payload, **kwargs):
        return SimpleNamespace(residual_categories=())

    def build_command_query(self, query, **kwargs):
        return runner.FIXED_COMMAND_QUERY


class FakePlaywrightContext:
    def __init__(self, browser):
        self.browser = browser

    async def __aenter__(self):
        return SimpleNamespace(chromium=SimpleNamespace())

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class ProQuestAtaiExplorationTests(unittest.TestCase):
    def test_fixed_query_and_database_state_are_closed_and_exact(self):
        self.assertEqual(
            runner._validate_fixed_query(runner.FIXED_COMMAND_QUERY),
            runner.FIXED_COMMAND_QUERY,
        )
        state = runner.freeze_database_label_state(
            [
                SimpleNamespace(label="B", checked=False),
                SimpleNamespace(label="A", checked=True),
            ]
        )
        self.assertEqual(state.entries, (("A", True), ("B", False)))
        self.assertEqual(state.selected_labels, frozenset({"A"}))
        self.assertNotEqual(
            runner.database_state_digest(state),
            runner.database_state_digest(
                runner.freeze_database_label_state(
                    [SimpleNamespace(label="A", checked=False), SimpleNamespace(label="B", checked=False)]
                )
            ),
        )
        with self.assertRaises(runner.InputValidationError):
            runner._validate_fixed_query('NOFT("CubeSat") AND YR(2011-2026)')

    def test_native_zero_is_accepted_only_with_zero_total_and_no_rows(self):
        payload = {
            "protocol": "https:",
            "host": "www.proquest.com",
            "titleExact": True,
            "productLinkExact": True,
            "queryFieldCount": 1,
            "queryMatches": True,
            "resultRoute": True,
            "routeClean": True,
            "pageOrdinal": 1,
            "totalNodeCount": 0,
            "totalText": "",
            "zeroResults": True,
            "rowCount": 0,
            "syntaxError": False,
            "blocked": False,
            "requiresAccess": False,
        }
        self.assertEqual(runner._parse_aggregate_result(payload), (0, True))
        with self.assertRaises(runner.StageFailure):
            runner._parse_aggregate_result({**payload, "rowCount": 1})

    def test_fake_live_flow_uses_one_page_one_native_submit_and_restores_exact_state(self):
        adapter = FakeAdapter()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            config = runner.ExplorationConfig(
                execute=True,
                cdp_url=runner.DEFAULT_CDP_URL,
                timeout_seconds=1.0,
                output_path=output,
            )
            status, receipt = runner.run_exploration(
                config,
                adapter=adapter,
                playwright_factory=lambda: FakePlaywrightContext(adapter._common.browser),
            )
            self.assertEqual(status, 0)
            self.assertEqual(receipt["result"]["total"], 3)
            self.assertFalse(receipt["result"]["native_zero"])
            self.assertEqual(receipt["submission"]["native_submit_count"], 1)
            self.assertEqual(receipt["submission"]["source_operation_count"], 1)
            self.assertTrue(receipt["controls"]["database_selection_controls_validated"])
            self.assertEqual(receipt["ownership"]["baseline_target_set_preserved"], True)
            self.assertEqual(receipt["ownership"]["owned_target_disappeared"], True)
            self.assertEqual(receipt["selection"]["restoration_status"], "attempted_verified")
            self.assertEqual(adapter.selection_submits, 2)
            self.assertEqual(adapter.selected["Unrelated database"], True)
            self.assertTrue(output.is_file())
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertNotIn("results", saved)
            saved_text = json.dumps(saved)
            self.assertNotIn(runner.FIXED_COMMAND_QUERY, saved_text)
            self.assertNotIn("https://www.proquest.com", saved_text)
            self.assertNotIn("anchor-target", saved_text)
            self.assertNotIn("owned-target", saved_text)

    def test_restoration_guard_does_not_overwrite_changed_selection(self):
        adapter = FakeAdapter()
        page = adapter._common.context.anchor
        page.url = runner.DATABASE_SELECTION_URL
        snapshot = runner.freeze_database_label_state(
            [
                SimpleNamespace(label=label, checked=checked)
                for label, checked in adapter.selected.items()
            ]
        )
        deliberate = runner.freeze_database_label_state(
            [
                SimpleNamespace(
                    label=label,
                    checked=label == runner.TARGET_DATABASE_LABEL,
                )
                for label in adapter.selected
            ]
        )
        adapter.selected["Unrelated database"] = False
        adapter.selected["Another database"] = True
        receipt = runner._empty_receipt(
            runner.ExplorationConfig(
                execute=True,
                cdp_url=runner.DEFAULT_CDP_URL,
                timeout_seconds=1.0,
                output_path=Path("unused.json"),
            )
        )

        async def no_op_reassert():
            return None

        restored = asyncio.run(
            runner._restore_selection_if_guarded(
                adapter,
                page,
                snapshot,
                deliberate,
                1.0,
                no_op_reassert,
                receipt,
            )
        )
        self.assertFalse(restored)
        self.assertFalse(receipt["selection"]["restoration_guard_passed"])
        self.assertEqual(adapter.selection_submits, 0)
        self.assertEqual(receipt["selection"]["restoration_status"], "not_attempted_state_changed")

    def test_dry_run_is_create_only_and_does_not_load_or_use_browser(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dry-run.json"
            config = runner.ExplorationConfig(
                execute=False,
                cdp_url=runner.DEFAULT_CDP_URL,
                timeout_seconds=1.0,
                output_path=output,
            )
            status, receipt = runner.run_exploration(config)
            self.assertEqual(status, 0)
            self.assertEqual(receipt["terminal"]["classification"], "dry_run")
            self.assertIsNone(receipt["result"]["total"])
            self.assertTrue(output.is_file())
            with self.assertRaises(runner.InputValidationError):
                runner.validate_output_path(output)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
