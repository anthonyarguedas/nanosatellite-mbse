"""Deterministic source-free tests for the WoS Core Collection P01 probe."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPTS = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


wos = load_module("test_wos_core_pilot_probe_module", "wos_core_pilot_probe.py")


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


def controls_payload(**overrides: bool) -> dict[str, bool]:
    payload = {
        "core_collection": True,
        "all_editions_button": True,
        "topic_field": True,
        "publication_date_button": True,
        "date_start_input": True,
        "date_end_input": True,
        "language_english": True,
        "document_type_absent": True,
        "query_input": True,
        "submit_button": True,
    }
    payload.update(overrides)
    return payload


def edition_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "dialog_present": True,
        "select_all_present": True,
        "select_all_checked": True,
        "individual_count": 10,
        "individual_checked_count": 10,
    }
    payload.update(overrides)
    return payload


class BasicControlsPage:
    def __init__(self, payloads: list[dict[str, bool]]) -> None:
        self.payloads = list(payloads)
        self.projection_calls = 0

    async def evaluate(self, script, *_args):
        self.assert_projection(script)
        self.projection_calls += 1
        if not self.payloads:
            raise AssertionError("unexpected basic-control projection")
        return self.payloads.pop(0)

    @staticmethod
    def assert_projection(script) -> None:
        if script != wos.BASIC_CONTROL_PROJECTION_SCRIPT:
            raise AssertionError("hydration must remain a passive control projection")


def result_payload(
    *,
    kind: str = "summary",
    total: int | None = 3,
    route_page: int | None = 1,
    current_page: int | None = 1,
    relevance: bool = True,
    page_size: bool = True,
    cards: int = 3,
    expected: int | None = 3,
    stable: str = "partial",
    export: bool = True,
    topic: bool = True,
    english: bool = True,
    publication_date: bool = True,
    document_type_absent: bool = True,
    challenge: bool = False,
    busy: bool = False,
    access: bool = False,
    syntax: bool = False,
) -> dict[str, object]:
    return {
        "classification": kind,
        "submitted_controls": {
            "topic": topic,
            "english": english,
            "publication_date": publication_date,
            "document_type_absent": document_type_absent,
        },
        "zero_alert": kind == "zero",
        "summary_route": kind == "summary",
        "source_total": total,
        "route_page": route_page,
        "current_page": current_page,
        "relevance": relevance,
        "page_size_50": page_size,
        "card_count": cards,
        "expected_card_count": expected,
        "stable_id_status": stable,
        "export_control_present": export,
        "challenge": challenge,
        "busy": busy,
        "access": access,
        "syntax_error": syntax,
    }


class FakeEditionLocator:
    def __init__(self, page: "FakeEditionPage") -> None:
        self.page = page

    @property
    def first(self) -> "FakeEditionLocator":
        return self

    async def count(self) -> int:
        self.page.edition_locator_checks += 1
        return 1 if self.page.edition_available else 0

    async def is_visible(self) -> bool:
        return self.page.edition_available

    async def click(self, **_kwargs) -> None:
        self.page.click_attempts += 1
        if self.page.click_attempts == 1:
            raise RuntimeError("hydration replaced edition node")
        self.page.events.append("edition")
        self.page.dialog_open = True


class FakeEditionKeyboard:
    def __init__(self, page: "FakeEditionPage") -> None:
        self.page = page

    async def press(self, key: str) -> None:
        self.page.events.append(key)
        if key != "Escape":
            raise AssertionError(key)
        self.page.dialog_open = False


class FakeEditionPage:
    def __init__(self) -> None:
        self.edition_locator_checks = 0
        self.click_attempts = 0
        self.dialog_open = False
        self.events: list[str] = []
        self.keyboard = FakeEditionKeyboard(self)

    @property
    def edition_available(self) -> bool:
        return self.edition_locator_checks >= 2

    def locator(self, selector: str) -> FakeEditionLocator:
        if selector != wos.EDITION_BUTTON_SELECTOR:
            raise AssertionError(f"unexpected selector: {selector}")
        return FakeEditionLocator(self)

    async def evaluate(self, script, *_args):
        if script != wos.EDITION_DIALOG_PROJECTION_SCRIPT:
            raise AssertionError("unexpected projection")
        return edition_payload(dialog_present=self.dialog_open)


class FakeDateInput:
    def __init__(self, page: "FakeDatePage", side: str) -> None:
        self.page = page
        self.side = side

    @property
    def first(self) -> "FakeDateInput":
        return self

    async def count(self) -> int:
        return int(self.page.custom_clicked)

    async def is_visible(self) -> bool:
        return self.page.custom_clicked

    async def fill(self, value: str) -> None:
        self.page.events.append(f"{self.side}={value}")
        self.page.values[self.side] = value

    async def input_value(self) -> str:
        return self.page.values[self.side]


class FakeDateButton:
    def __init__(self, page: "FakeDatePage", name: str) -> None:
        self.page = page
        self.name = name

    @property
    def first(self) -> "FakeDateButton":
        return self

    async def count(self) -> int:
        return 1

    async def is_visible(self) -> bool:
        if self.name == "Add Date Range":
            return not self.page.add_clicked
        return self.page.add_clicked and not self.page.publication_clicked

    async def get_attribute(self, attribute: str) -> str:
        if attribute == "aria-label":
            return self.name
        return ""

    async def inner_text(self) -> str:
        return self.name

    async def click(self, **_kwargs) -> None:
        self.page.events.append(self.name)
        if self.name == "Add Date Range":
            self.page.add_clicked = True
        else:
            self.page.publication_clicked = True


class FakeDateButtons:
    def __init__(self, page: "FakeDatePage") -> None:
        self.page = page

    async def count(self) -> int:
        return 2

    def nth(self, index: int) -> FakeDateButton:
        return self.page.buttons[index]


class FakeCustomDateOption:
    def __init__(self, page: "FakeDatePage") -> None:
        self.page = page

    @property
    def first(self) -> "FakeCustomDateOption":
        return self

    async def count(self) -> int:
        return int(self.page.publication_clicked)

    async def is_visible(self) -> bool:
        return self.page.publication_clicked and not self.page.custom_clicked

    async def click(self, **_kwargs) -> None:
        self.page.events.append("Custom")
        self.page.custom_clicked = True


class FakeDatePage:
    def __init__(self) -> None:
        self.add_clicked = False
        self.publication_clicked = False
        self.custom_clicked = False
        self.values = {"start": "", "end": ""}
        self.events: list[str] = []
        self.buttons = [
            FakeDateButton(self, "Add Date Range"),
            FakeDateButton(self, "Publication Date"),
        ]

    def locator(self, selector: str):
        if selector == wos.DATE_START_SELECTOR:
            return FakeDateInput(self, "start")
        if selector == wos.DATE_END_SELECTOR:
            return FakeDateInput(self, "end")
        if selector == wos.CUSTOM_DATE_OPTION_SELECTOR:
            return FakeCustomDateOption(self)
        if selector == "button":
            return FakeDateButtons(self)
        raise AssertionError(f"unexpected selector: {selector}")


class ResultPage:
    def __init__(self, states: list[dict[str, object]]) -> None:
        self.states = list(states)
        self.scroll_calls = 0

    async def evaluate(self, script, *_args):
        if script == wos.POST_RESULT_PROJECTION_SCRIPT:
            if not self.states:
                raise AssertionError("unexpected result projection")
            return self.states.pop(0)
        if script == wos.SCROLL_TO_BOTTOM_SCRIPT:
            self.scroll_calls += 1
            return True
        raise AssertionError("unexpected script")


class TranslationArtifactTests(unittest.TestCase):
    PACKET = SCRIPTS.parent / "searches" / "sources" / "s-d02-web-of-science"
    PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")

    def test_all_nine_topic_cells_are_hash_bound_and_lossless(self):
        dictionary = json.loads(
            (SCRIPTS.parent / "searches" / "search-concept-dictionary.json").read_text(
                encoding="utf-8"
            )
        )
        spec = json.loads((self.PACKET / "translation-spec.json").read_text(encoding="utf-8"))
        self.assertEqual(
            [item["partition_id"] for item in spec["semantic_partitions"]],
            list(self.PARTITIONS),
        )
        for partition in spec["semantic_partitions"]:
            with self.subTest(partition=partition["partition_id"]):
                self.assertEqual(len(partition["source_native_cells"]), 1)
                self.assertFalse(partition["lossless_union"]["required"])
                cell = partition["source_native_cells"][0]
                path = self.PACKET / cell["exact_query_file"]
                data = path.read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), cell["sha256"])
                text = data.decode("utf-8")
                self.assertTrue(text.startswith("TS=("))
                self.assertNotIn("*", text)

        # A1 is the P01 non-pair query; BT2 retains every declared T2 pair.
        a1 = (self.PACKET / "queries" / "A1.wos-topic.txt").read_text(encoding="utf-8")
        bt2 = (self.PACKET / "queries" / "BT2.wos-topic.txt").read_text(encoding="utf-8")
        self.assertNotIn("NEAR/6", a1)
        self.assertEqual(bt2.count(" NEAR/6 "), len(dictionary["concepts"]["T2"]["left"]) * 4)
        for term in dictionary["concepts"]["P"]["terms"]:
            self.assertIn(f'"{term}"', a1)


class BasicControlHydrationTests(unittest.TestCase):
    def test_false_controls_are_polled_until_hydrated(self):
        page = BasicControlsPage(
            [
                controls_payload(
                    core_collection=False,
                    all_editions_button=False,
                    topic_field=False,
                    publication_date_button=False,
                    query_input=False,
                    submit_button=False,
                ),
                controls_payload(),
            ]
        )
        clock = FakeClock()
        outcome = asyncio.run(
            wos.wait_for_basic_controls(
                page,
                timeout_seconds=1.0,
                poll_interval_seconds=0.25,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertFalse(outcome.timed_out)
        self.assertEqual(outcome.polls, 2)
        self.assertIsNotNone(outcome.controls)
        self.assertTrue(outcome.controls.hydrated)
        self.assertEqual(page.projection_calls, 2)
        self.assertEqual(clock.sleeps, [0.25])

    def test_basic_control_hydration_timeout_is_passive_and_terminal(self):
        page = BasicControlsPage(
            [controls_payload(core_collection=False)] * 4
        )
        clock = FakeClock()
        outcome = asyncio.run(
            wos.wait_for_basic_controls(
                page,
                timeout_seconds=0.5,
                poll_interval_seconds=0.25,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertTrue(outcome.timed_out)
        self.assertIsNone(outcome.controls)
        self.assertEqual(outcome.polls, 2)
        self.assertEqual(page.projection_calls, 2)
        self.assertEqual(clock.sleeps, [0.25, 0.25])


class ControlTimingTests(unittest.TestCase):
    def test_edition_selector_waits_and_retries_same_exact_control(self):
        page = FakeEditionPage()
        clock = FakeClock()
        state = asyncio.run(
            wos.verify_all_editions(
                page,
                timeout=0.8,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertTrue(state.all_current_editions_checked)
        self.assertEqual(page.click_attempts, 2)
        self.assertEqual(page.events, ["edition", "Escape"])
        self.assertEqual(clock.sleeps, [0.2, 0.2])
        self.assertGreaterEqual(page.edition_locator_checks, 3)

    def test_date_setup_adds_range_then_publication_date_before_exact_inputs(self):
        page = FakeDatePage()
        clock = FakeClock()
        asyncio.run(
            wos.ensure_date_range(
                page,
                "2026-08-25",
                timeout=0.8,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(
            page.events,
            [
                "Add Date Range",
                "Publication Date",
                "Custom",
                "start=2011-01-01",
                "end=2026-08-25",
            ],
        )
        self.assertEqual(page.values, {"start": "2011-01-01", "end": "2026-08-25"})
        self.assertEqual(clock.sleeps, [])


class ResultProjectionTests(unittest.TestCase):
    def test_control_and_edition_projection_requires_all_current_editions(self):
        controls = wos.controls_from_payload(controls_payload())
        editions = wos.edition_state_from_payload(edition_payload())
        self.assertTrue(controls.ready)
        self.assertTrue(editions.all_current_editions_checked)
        unchecked = wos.edition_state_from_payload(
            edition_payload(individual_checked_count=9)
        )
        self.assertFalse(unchecked.all_current_editions_checked)

    def test_zero_is_distinct_from_summary_and_requires_echoed_controls(self):
        zero = wos.result_state_from_payload(result_payload(kind="zero", total=0, cards=0, expected=None))
        self.assertEqual(wos._result_classification(zero), "zero_observed")
        summary = wos.result_state_from_payload(result_payload())
        self.assertIsNone(wos._result_classification(summary))
        no_echo = wos.result_state_from_payload(result_payload(topic=False))
        self.assertEqual(wos._result_classification(no_echo), "summary_controls_unverified")
        no_relevance = wos.result_state_from_payload(result_payload(relevance=False))
        self.assertEqual(wos._result_classification(no_relevance), "summary_controls_unverified")

    def test_result_projection_keeps_only_aggregate_stable_id_and_export_facts(self):
        state = wos.result_state_from_payload(
            result_payload(stable="uniform", export=False, total=51, cards=1, expected=50)
        )
        self.assertEqual(state.stable_id_status, "uniform")
        self.assertFalse(state.export_control_present)
        self.assertEqual(state.source_total, 51)
        encoded = json.dumps(state.__dict__, default=lambda value: value.__dict__)
        self.assertNotIn("opaque", encoded)
        self.assertNotIn("query", encoded)

    def test_summary_page_identity_is_fail_closed(self):
        state = wos.result_state_from_payload(result_payload(route_page=2, current_page=2))
        self.assertEqual(wos._result_classification(state), "summary_page_identity_failed")

    def test_bounded_lazy_card_hydration_requires_two_equal_complete_samples(self):
        page = ResultPage(
            [
                result_payload(cards=1, expected=3),
                result_payload(cards=3, expected=3),
                result_payload(cards=3, expected=3),
            ]
        )
        clock = FakeClock()
        outcome = asyncio.run(
            wos.wait_for_result_and_hydrate(
                page,
                timeout_seconds=2.0,
                poll_interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(outcome.classification, "summary_observed")
        self.assertEqual(outcome.state.source_total, 3)
        self.assertEqual(outcome.scrolls, 1)
        self.assertEqual(page.scroll_calls, 1)

    def test_challenge_and_busy_never_reissue_or_scroll(self):
        for flag, expected in (("challenge", "challenge_detected"), ("busy", "busy_detected")):
            kwargs = {flag: True}
            page = ResultPage([result_payload(**kwargs)])
            outcome = asyncio.run(
                wos.wait_for_result_and_hydrate(
                    page,
                    timeout_seconds=1.0,
                    poll_interval_seconds=0.1,
                )
            )
            self.assertEqual(outcome.classification, expected)
            self.assertEqual(page.scroll_calls, 0)

    def test_incomplete_lazy_cards_end_as_null_failure(self):
        page = ResultPage([result_payload(cards=1, expected=3)] * 3)
        clock = FakeClock()
        outcome = asyncio.run(
            wos.wait_for_result_and_hydrate(
                page,
                timeout_seconds=0.2,
                poll_interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(outcome.classification, "summary_card_hydration_failed")
        self.assertTrue(outcome.timed_out)


class TargetSession:
    def __init__(self, browser: "FakeBrowser", page: "FakePage | None" = None) -> None:
        self.browser = browser
        self.page = page

    async def send(self, method: str):
        if method == "Target.getTargetInfo":
            return {"targetInfo": {"targetId": self.page.target_id}}
        if method == "Target.getTargets":
            return {"targetInfos": self.browser.target_infos()}
        raise AssertionError(method)

    async def detach(self) -> None:
        return None


class FakePage:
    def __init__(self, context: "FakeContext", target_id: str) -> None:
        self.context = context
        self.target_id = target_id
        self.closed = False
        self.goto_calls: list[tuple[object, dict]] = []
        self.url = wos.BASIC_SEARCH_URL

    def is_closed(self) -> bool:
        return self.closed

    async def goto(self, *args, **kwargs):
        self.goto_calls.append((args, kwargs))
        return SimpleNamespace(status=200)

    async def close(self) -> None:
        self.closed = True
        if self in self.context.pages:
            self.context.pages.remove(self)


class FakeContext:
    def __init__(self, session: "FakePlaywright") -> None:
        self.session = session
        self.baseline = [FakePage(self, "baseline-target")]
        self.pages = list(self.baseline)
        self.created: FakePage | None = None

    async def new_page(self) -> FakePage:
        self.created = FakePage(self, "owned-target")
        self.pages.append(self.created)
        return self.created

    async def new_cdp_session(self, page: FakePage) -> TargetSession:
        return TargetSession(self.session.browser, page)


class FakeBrowser:
    def __init__(self, session: "FakePlaywright") -> None:
        self.session = session
        self.context = FakeContext(session)
        self.contexts = [self.context]

    def target_infos(self):
        return [{"type": "page", "targetId": page.target_id} for page in self.context.pages]

    async def new_browser_cdp_session(self) -> TargetSession:
        return TargetSession(self, None)


class FakeChromium:
    def __init__(self, session: "FakePlaywright") -> None:
        self.session = session
        self.calls: list[str] = []

    async def connect_over_cdp(self, endpoint: str, **kwargs):
        self.calls.append(endpoint)
        return self.session.browser


class FakePlaywright:
    def __init__(self) -> None:
        self.browser = FakeBrowser(self)
        self.chromium = FakeChromium(self)
        self.live = False

    async def __aenter__(self):
        self.live = True
        return self

    async def __aexit__(self, *_args):
        self.live = False
        return False


def probe_config(path: Path, *, execute: bool = True) -> wos.ProbeConfig:
    query = 'TS=("CubeSat")'
    return wos.ProbeConfig(
        execute=execute,
        cdp_url=wos.DEFAULT_CDP_URL,
        query=query,
        query_file_name="A1.wos-topic.txt",
        query_sha256=hashlib.sha256(query.encode()).hexdigest(),
        date_upper="2026-08-25",
        timeout_seconds=1.0,
        poll_interval_seconds=0.1,
        receipt_path=path,
    )


class OwnershipAndOfflineLifecycleTests(unittest.TestCase):
    def test_dry_run_writes_create_only_receipt_without_playwright(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("dry-run must not start Playwright")

            status, receipt = asyncio.run(
                wos.run_probe(probe_config(path, execute=False), playwright_factory=forbidden_factory)
            )
            self.assertEqual(status, 0)
            self.assertFalse(called)
            self.assertEqual(receipt["result"]["classification"], "dry_run")
            self.assertTrue(path.is_file())
            self.assertNotIn('TS=("CubeSat")', path.read_text())
            with self.assertRaises(FileExistsError):
                wos.reserve_output_path(path)

    def test_one_owned_page_submits_once_and_restores_baseline(self):
        session = FakePlaywright()
        controls = wos.BasicControlState(
            True, True, True, True, True, True, True, True, True, True
        )
        editions = wos.EditionState(True, True, True, 10, 10)
        result = wos.ResultState(
            "summary",
            wos.SubmittedControls(True, True, True, True),
            False,
            True,
            3,
            1,
            1,
            True,
            True,
            3,
            3,
            "partial",
            True,
            False,
            False,
            False,
            False,
        )
        hydration = wos.HydrationOutcome(result, "summary_observed", 2, 0, False)
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            wos,
            "wait_for_basic_controls",
            new=mock.AsyncMock(
                return_value=wos.BasicControlHydrationOutcome(controls, 1, False)
            ),
        ), mock.patch.object(
            wos, "prepare_basic_controls", new=mock.AsyncMock(return_value=(controls, editions))
        ), mock.patch.object(
            wos, "submit_one_query", new=mock.AsyncMock()
        ), mock.patch.object(
            wos, "wait_for_result_and_hydrate", new=mock.AsyncMock(return_value=hydration)
        ):
            status, receipt = asyncio.run(
                wos.run_probe(
                    probe_config(Path(directory) / "receipt.json"),
                    playwright_factory=lambda: session,
                )
            )
        self.assertEqual(status, 0)
        self.assertEqual(receipt["result"]["classification"], "summary_observed")
        self.assertEqual(receipt["submission"]["source_operation_count"], 1)
        self.assertEqual(len(session.browser.context.created.goto_calls), 1)
        self.assertEqual(session.browser.context.pages, session.browser.context.baseline)
        self.assertTrue(receipt["ownership"]["owned_target_disappeared"])
        self.assertTrue(receipt["ownership"]["baseline_target_set_preserved"])
        self.assertTrue(session.browser.context.created.closed)
        encoded = json.dumps(receipt)
        self.assertNotIn("owned-target", encoded)
        self.assertNotIn("TS=(", encoded)

    def test_hydration_timeout_keeps_submit_zero_and_cleans_owned_page(self):
        session = FakePlaywright()
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            wos,
            "wait_for_basic_controls",
            new=mock.AsyncMock(
                return_value=wos.BasicControlHydrationOutcome(None, 4, True)
            ),
        ) as wait_for_controls, mock.patch.object(
            wos, "prepare_basic_controls", new=mock.AsyncMock()
        ) as prepare, mock.patch.object(
            wos, "submit_one_query", new=mock.AsyncMock()
        ) as submit:
            status, receipt = asyncio.run(
                wos.run_probe(
                    probe_config(Path(directory) / "receipt.json"),
                    playwright_factory=lambda: session,
                )
            )
        self.assertEqual(status, 1)
        self.assertEqual(receipt["result"]["classification"], "basic_controls_not_ready")
        self.assertEqual(receipt["submission"]["source_operation_count"], 0)
        self.assertFalse(receipt["submission"]["native_submit_observed"])
        self.assertEqual(receipt["controls"]["basic_hydration_polls"], 4)
        self.assertTrue(receipt["controls"]["basic_hydration_timed_out"])
        wait_for_controls.assert_awaited_once()
        prepare.assert_not_awaited()
        submit.assert_not_awaited()
        self.assertTrue(receipt["ownership"]["owned_target_disappeared"])
        self.assertTrue(receipt["ownership"]["baseline_target_set_preserved"])
        self.assertEqual(session.browser.context.pages, session.browser.context.baseline)

    def test_wrong_endpoint_is_rejected_before_factory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = probe_config(Path(directory) / "receipt.json")
            config = wos.ProbeConfig(**{**config.__dict__, "cdp_url": "http://127.0.0.1:9223"})
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("wrong endpoint must not connect")

            status, receipt = asyncio.run(wos.run_probe(config, playwright_factory=forbidden_factory))
            self.assertEqual(status, 1)
            self.assertFalse(called)
            self.assertEqual(receipt["result"]["classification"], "invalid_runtime_config")

    def test_cli_help_is_offline(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "wos_core_pilot_probe.py"), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("--receipt", completed.stdout)
        self.assertIn("--query-file", completed.stdout)


if __name__ == "__main__":
    unittest.main()
