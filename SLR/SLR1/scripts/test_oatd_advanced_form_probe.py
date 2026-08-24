"""Deterministic offline tests for the OATD advanced-form diagnostic."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from unittest import mock


SCRIPTS = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:  # pragma: no cover - test setup
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


oatd = load_module(
    "test_oatd_advanced_form_probe_module", "oatd_advanced_form_probe.py"
)


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


class StatePage:
    """A no-network page double for post-click state-machine tests."""

    def __init__(self, states: list[object], fallback: object | None = None) -> None:
        self.states = list(states)
        self.fallback = fallback if fallback is not None else unknown_state()
        self.goto_calls: list[tuple[object, dict]] = []

    async def evaluate(self, *_args, **_kwargs):
        if self.states:
            item = self.states.pop(0)
        else:
            item = self.fallback
        if isinstance(item, BaseException):
            raise item
        return item

    async def goto(self, *args, **kwargs):
        self.goto_calls.append((args, kwargs))


def post_state(
    *,
    challenge: bool = False,
    busy: bool = False,
    access: bool = False,
    syntax: bool = False,
    route: bool = True,
    identity: bool = True,
    readback: bool = True,
    kind: str = "unknown",
    total: int | None = None,
    observed: bool = False,
) -> dict:
    return {
        "challenge": challenge,
        "busy": busy,
        "access": access,
        "syntax_error": syntax,
        "canonical_advanced_route": route,
        "source_identity": identity,
        "form_readback_exact": readback,
        "result_kind": kind,
        "source_total": total,
        "result_observed": observed,
    }


def result_state(total: int = 2) -> dict:
    return post_state(kind="range", total=total, observed=True)


def zero_state() -> dict:
    return post_state(kind="zero", total=0, observed=True)


def unknown_state() -> dict:
    return post_state(route=False, readback=False)


def busy_state(
    *, route: bool = True, identity: bool = True, readback: bool = True
) -> dict:
    return post_state(busy=True, route=route, identity=identity, readback=readback)


def budget(retries: int = 2, delay: float = 1.0):
    return oatd.BusyRetryBudget(max_retries=retries, initial_delay_seconds=delay)


class TargetSession:
    def __init__(
        self, browser: "LeaseBrowser", page: "LeasePage | None" = None
    ) -> None:
        self.browser = browser
        self.page = page
        self.detached = False

    async def send(self, method: str):
        if method == "Target.getTargetInfo":
            assert self.page is not None
            return {"targetInfo": {"targetId": self.page.target_id}}
        if method == "Target.getTargets":
            return {
                "targetInfos": [
                    {"type": "page", "targetId": page.target_id}
                    for page in self.browser.target_pages()
                ]
            }
        raise AssertionError(method)

    async def detach(self) -> None:
        self.detached = True


class LeasePage:
    def __init__(
        self,
        context: "LeaseContext",
        target_id: str,
        *,
        close_raises: bool = False,
    ) -> None:
        self.context = context
        self.target_id = target_id
        self.close_raises = close_raises
        self.closed = False
        self.close_calls = 0
        self.close_while_live: bool | None = None
        self.goto_calls: list[tuple[object, dict]] = []

    def is_closed(self) -> bool:
        return self.closed

    async def close(self) -> None:
        self.close_calls += 1
        self.close_while_live = self.context.session.live
        if self.close_raises:
            raise RuntimeError("offline close failure")
        self.closed = True
        if self in self.context.pages:
            self.context.pages.remove(self)
        if self.context.mutate_baseline_on_owned_close and self.context.baselines:
            baseline = self.context.baselines[0]
            if baseline in self.context.pages:
                self.context.pages.remove(baseline)

    async def goto(self, *args, **kwargs) -> None:
        self.goto_calls.append((args, kwargs))


class LeaseContext:
    def __init__(
        self,
        session: "LeasePlaywright",
        baseline_count: int = 2,
        *,
        close_raises: bool = False,
        mutate_baseline_on_owned_close: bool = False,
    ) -> None:
        self.session = session
        self.close_raises = close_raises
        self.mutate_baseline_on_owned_close = mutate_baseline_on_owned_close
        self.baselines = [
            LeasePage(self, f"baseline-{number}") for number in range(baseline_count)
        ]
        self.pages = list(self.baselines)
        self.created: LeasePage | None = None
        self.new_page_calls = 0

    async def new_page(self) -> LeasePage:
        self.new_page_calls += 1
        self.created = LeasePage(
            self, "owned-target-secret", close_raises=self.close_raises
        )
        self.pages.append(self.created)
        return self.created

    async def new_cdp_session(self, page: LeasePage) -> TargetSession:
        return TargetSession(self.session.browser, page)


class LeaseBrowser:
    def __init__(
        self, context: LeaseContext, *, retain_closed_target: bool = False
    ) -> None:
        self.contexts = [context]
        self.context = context
        self.retain_closed_target = retain_closed_target

    def target_pages(self) -> list[LeasePage]:
        pages = list(self.context.pages)
        if self.retain_closed_target and self.context.created is not None:
            if self.context.created not in pages:
                pages.append(self.context.created)
        return pages

    async def new_browser_cdp_session(self) -> TargetSession:
        return TargetSession(self)


class LeaseChromium:
    def __init__(self, session: "LeasePlaywright") -> None:
        self.session = session
        self.calls: list[tuple[str, dict]] = []

    async def connect_over_cdp(self, endpoint: str, **kwargs) -> LeaseBrowser:
        assert self.session.live
        self.calls.append((endpoint, kwargs))
        return self.session.browser


class LeasePlaywright:
    def __init__(
        self,
        *,
        close_raises: bool = False,
        retain_closed_target: bool = False,
        mutate_baseline_on_owned_close: bool = False,
        baseline_count: int = 2,
    ) -> None:
        self.live = False
        self.context = LeaseContext(
            self,
            baseline_count,
            close_raises=close_raises,
            mutate_baseline_on_owned_close=mutate_baseline_on_owned_close,
        )
        self.browser = LeaseBrowser(
            self.context, retain_closed_target=retain_closed_target
        )
        self.chromium = LeaseChromium(self)

    async def __aenter__(self):
        self.live = True
        return self

    async def __aexit__(self, *_args):
        self.live = False
        return False


def config(tmp: Path, *, execute: bool = True) -> object:
    return oatd.ProbeConfig(
        execute=execute,
        cdp_url="http://127.0.0.1:9222",
        query="private query phrase",
        field_label="Title",
        timeout_seconds=1.0,
        poll_interval_seconds=0.1,
        busy_retries=2,
        busy_retry_delay_seconds=1.0,
        output_path=tmp / "receipt.json",
    )


def valid_inspection(source_state: str | None = None):
    return oatd.FormInspection(
        source_state=source_state,
        canonical_form_count=1,
        form_index=0,
        method_get=True,
        box1_count=1,
        field1_count=1,
        matching_field_option_count=1,
        field_value="title",
        visible_native_submit_count=1,
    )


def safety_payload(**overrides: bool) -> dict[str, bool]:
    payload = {name: True for name in oatd.PRE_CLICK_SAFETY_FIELDS}
    payload.update(overrides)
    return payload


def valid_safety() -> oatd.PreClickSafety:
    return oatd.pre_click_safety_from_payload(safety_payload())


def valid_prepared():
    return oatd.PreparedSubmission(
        retry_parameters=(("box1", "private query phrase"), ("field1", "title")),
        visible_native_submit_count=1,
        pre_click_safety=valid_safety(),
    )


class OATDPostClickStateMachineTests(unittest.TestCase):
    def run_wait(self, page: StatePage, *, retries: int = 2, timeout: float = 1.0):
        clock = FakeClock()
        outcome = asyncio.run(
            oatd.wait_for_post_click_state(
                page,
                query="private query phrase",
                field_value="title",
                retry_parameters=(
                    ("box1", "private query phrase"),
                    ("field1", "title"),
                ),
                timeout_seconds=timeout,
                poll_interval_seconds=0.1,
                busy_budget=budget(retries),
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        return outcome, clock

    def test_result_and_zero_are_distinct_terminal_observations(self):
        result, _ = self.run_wait(StatePage([result_state(7)]))
        zero, _ = self.run_wait(StatePage([zero_state()]))
        self.assertEqual(
            (result.classification, result.source_total), ("result_observed", 7)
        )
        self.assertEqual((zero.classification, zero.source_total), ("zero_observed", 0))

    def test_challenge_is_passive_and_never_reissues(self):
        page = StatePage([post_state(challenge=True), result_state(3)])
        outcome, clock = self.run_wait(page)
        self.assertEqual(outcome.classification, "result_observed")
        self.assertEqual(page.goto_calls, [])
        self.assertEqual(clock.sleeps, [0.1])

    def test_finite_busy_revalidates_then_reissues_only_canonical_controls(self):
        page = StatePage([busy_state(), busy_state(), result_state(4)])
        outcome, clock = self.run_wait(page)
        self.assertEqual(outcome.classification, "result_observed")
        self.assertEqual(outcome.busy_retries_performed, 1)
        self.assertEqual(len(page.goto_calls), 1)
        self.assertEqual(clock.sleeps, [1.0])
        retry_url = page.goto_calls[0][0][0]
        self.assertTrue(retry_url.startswith(oatd.ADVANCED_ACTION + "?"))
        self.assertIn("box1=private+query+phrase", retry_url)
        self.assertIn("field1=title", retry_url)

    def test_busy_that_clears_during_respectful_wait_is_not_reissued(self):
        page = StatePage([busy_state(), result_state(2)])
        outcome, _ = self.run_wait(page)
        self.assertEqual(outcome.classification, "result_observed")
        self.assertEqual(outcome.busy_retries_performed, 0)
        self.assertEqual(page.goto_calls, [])

    def test_persistent_busy_exhausts_a_finite_budget(self):
        page = StatePage([busy_state(), busy_state(), busy_state()])
        outcome, _ = self.run_wait(page, retries=1)
        self.assertEqual(outcome.classification, "busy_after_submission")
        self.assertEqual(outcome.busy_retries_performed, 1)
        self.assertEqual(len(page.goto_calls), 1)

    def test_busy_with_unverified_form_state_is_not_reissued(self):
        page = StatePage([busy_state(route=False, readback=False)])
        outcome, _ = self.run_wait(page)
        self.assertEqual(outcome.classification, "busy_after_submission")
        self.assertEqual(page.goto_calls, [])

    def test_busy_without_source_identity_is_not_reissued(self):
        page = StatePage([busy_state(identity=False)])
        outcome, _ = self.run_wait(page)
        self.assertEqual(outcome.classification, "busy_after_submission")
        self.assertEqual(page.goto_calls, [])

    def test_throwing_busy_retry_accounts_dispatch_before_goto_returns(self):
        class ThrowingGotoPage(StatePage):
            async def goto(self, *args, **kwargs):
                self.goto_calls.append((args, kwargs))
                raise RuntimeError("offline dispatched goto failure")

        page = ThrowingGotoPage([busy_state(), busy_state()])
        outcome, _ = self.run_wait(page)
        self.assertEqual(outcome.classification, "busy_retry_navigation_failed")
        self.assertEqual(outcome.busy_retries_attempted, 1)
        self.assertEqual(outcome.busy_retries_completed, 0)
        self.assertEqual(outcome.busy_retries_performed, 1)
        self.assertEqual(len(page.goto_calls), 1)

    def test_syntax_access_challenge_and_unobserved_timeout_are_distinct(self):
        syntax, _ = self.run_wait(StatePage([post_state(syntax=True)]))
        access, _ = self.run_wait(StatePage([post_state(access=True)]))
        challenge, _ = self.run_wait(
            StatePage(
                [post_state(challenge=True)], fallback=post_state(challenge=True)
            ),
            timeout=0.2,
        )
        timeout, _ = self.run_wait(StatePage([], fallback=unknown_state()), timeout=0.2)
        self.assertEqual(syntax.classification, "syntax_after_submission")
        self.assertEqual(access.classification, "access_after_submission")
        self.assertEqual(challenge.classification, "challenge_after_submission")
        self.assertEqual(timeout.classification, "submission_not_observed_timeout")

    def test_challenge_appearing_during_busy_revalidation_is_not_reissued(self):
        page = StatePage([busy_state(), post_state(challenge=True), result_state(2)])
        outcome, _ = self.run_wait(page)
        self.assertEqual(outcome.classification, "result_observed")
        self.assertEqual(page.goto_calls, [])


class OATDFormPreparationTests(unittest.TestCase):
    def inventory(self, *, unexpected: int = 0) -> dict:
        entries = []
        for name in oatd.RETRY_CONTROL_NAMES:
            if name == "box1":
                entries.append(
                    {
                        "name": name,
                        "count": 1,
                        "tag": "input",
                        "type": "text",
                        "value": "private query phrase",
                        "checked": False,
                        "disabled": False,
                    }
                )
            elif name == "field1":
                entries.append(
                    {
                        "name": name,
                        "count": 1,
                        "tag": "select",
                        "type": "select-one",
                        "value": "title",
                        "checked": False,
                        "disabled": False,
                    }
                )
            else:
                entries.append(
                    {
                        "name": name,
                        "count": 0,
                        "tag": "",
                        "type": "",
                        "value": "",
                        "checked": False,
                        "disabled": False,
                    }
                )
        return {"unexpected_data_control_count": unexpected, "entries": entries}

    def test_retry_url_comes_only_from_prevalidated_controls(self):
        parameters = oatd.retry_parameters_from_inventory(
            self.inventory(), query="private query phrase", field_value="title"
        )
        self.assertEqual(
            parameters, (("box1", "private query phrase"), ("field1", "title"))
        )
        self.assertEqual(
            oatd.canonical_retry_url(parameters),
            oatd.ADVANCED_ACTION + "?box1=private+query+phrase&field1=title",
        )

    def test_unknown_or_changed_retry_controls_fail_closed(self):
        with self.assertRaises(oatd.ProbeAbort):
            oatd.retry_parameters_from_inventory(
                self.inventory(unexpected=1),
                query="private query phrase",
                field_value="title",
            )
        changed = self.inventory()
        changed["entries"][1]["value"] = "different"
        with self.assertRaises(oatd.ProbeAbort):
            oatd.retry_parameters_from_inventory(
                changed, query="private query phrase", field_value="title"
            )

    def test_native_submission_uses_one_visible_locator_click(self):
        inventory = self.inventory()

        class Control:
            def __init__(self, value: str = "") -> None:
                self.value = value
                self.clicked = 0
                self.selected: str | None = None

            async def count(self):
                return 1

            async def is_visible(self):
                return True

            async def fill(self, value):
                self.value = value

            async def select_option(self, value):
                self.selected = value
                self.value = value

            async def input_value(self):
                return self.value

            async def click(self):
                self.clicked += 1

            @property
            def first(self):
                return self

        class Form:
            def __init__(self, safety: dict | None = None) -> None:
                self.box = Control()
                self.field = Control()
                self.submit = Control()
                self.safety = safety or safety_payload()

            async def evaluate(self, script, *_args):
                if script == oatd.FORM_SELF_CHECK_SCRIPT:
                    return {
                        "canonical_form_count": 1,
                        "selected_form_is_canonical": True,
                    }
                if script == oatd.FORM_CONTROL_INVENTORY_SCRIPT:
                    return inventory
                if script == oatd.PRE_CLICK_SAFETY_SCRIPT:
                    return self.safety
                raise AssertionError("unexpected form script")

            def locator(self, selector):
                if "box1" in selector:
                    return self.box
                if "field1" in selector:
                    return self.field
                if selector == oatd.NATIVE_SUBMIT_SELECTOR:
                    return self.submit
                raise AssertionError(selector)

        class Forms:
            async def count(self):
                return 1

            def nth(self, _index):
                return form

        class Page:
            def locator(self, selector):
                if selector != "form":
                    raise AssertionError(selector)
                return Forms()

        form = Form()
        prepared = asyncio.run(
            oatd.prepare_native_submission(
                Page(), valid_inspection(), "private query phrase"
            )
        )
        self.assertEqual(form.box.value, "private query phrase")
        self.assertEqual(form.field.selected, "title")
        self.assertEqual(form.submit.clicked, 1)
        self.assertEqual(prepared.visible_native_submit_count, 1)
        self.assertTrue(prepared.pre_click_safety.verified)

        for requirement in oatd.PRE_CLICK_SAFETY_FIELDS:
            with self.subTest(requirement=requirement):
                form = Form(safety_payload(**{requirement: False}))
                with self.assertRaises(oatd.PreClickSafetyFailure):
                    asyncio.run(
                        oatd.prepare_native_submission(
                            Page(), valid_inspection(), "private query phrase"
                        )
                    )
                self.assertEqual(form.submit.clicked, 0)

    def test_pre_click_safety_accepts_only_boolean_route_and_submit_proof(self):
        self.assertTrue(oatd.pre_click_safety_from_payload(safety_payload()).verified)
        for requirement in oatd.PRE_CLICK_SAFETY_FIELDS:
            with self.subTest(requirement=requirement):
                safety = oatd.pre_click_safety_from_payload(
                    safety_payload(**{requirement: False})
                )
                self.assertFalse(safety.verified)
        malformed = safety_payload()
        malformed["form_target_self"] = "_self"
        with self.assertRaises(oatd.ProbeAbort):
            oatd.pre_click_safety_from_payload(malformed)

    def test_source_never_uses_programmatic_form_submission_or_navigation_wait(self):
        source = (SCRIPTS / "oatd_advanced_form_probe.py").read_text(encoding="utf-8")
        self.assertNotIn("request" + "Submit", source)
        self.assertNotIn("expect_" + "navigation", source)


class OATDOwnershipAndCleanupTests(unittest.TestCase):
    def run_lifecycle(
        self,
        session: LeasePlaywright,
        *,
        inspection=None,
        post_click_outcome: oatd.PostClickOutcome | None = None,
    ):
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / "receipt.json"
            fake_clock = FakeClock()
            with (
                mock.patch.object(
                    oatd,
                    "inspect_advanced_form",
                    new=mock.AsyncMock(return_value=inspection or valid_inspection()),
                ),
                mock.patch.object(
                    oatd,
                    "prepare_native_submission",
                    new=mock.AsyncMock(return_value=valid_prepared()),
                ),
                mock.patch.object(
                    oatd,
                    "wait_for_post_click_state",
                    new=mock.AsyncMock(
                        return_value=post_click_outcome
                        or oatd.PostClickOutcome("result_observed", 5, 1, 0, 0)
                    ),
                ),
            ):
                return asyncio.run(
                    oatd.run_probe(
                        config(receipt_path.parent),
                        playwright_factory=lambda: session,
                        clock=fake_clock,
                        sleeper=fake_clock.sleep,
                    )
                )

    def test_owned_page_is_distinct_and_all_baselines_survive(self):
        session = LeasePlaywright(baseline_count=3)
        status, receipt = self.run_lifecycle(session)
        owned = session.context.created
        self.assertEqual(status, 0)
        self.assertTrue(receipt["ownership"]["owned_page_distinct_from_baseline"])
        self.assertTrue(receipt["ownership"]["owned_target_disappeared"])
        self.assertTrue(receipt["ownership"]["baseline_pages_preserved"])
        self.assertEqual(session.context.pages, session.context.baselines)
        self.assertTrue(all(not page.is_closed() for page in session.context.baselines))
        self.assertEqual(session.context.new_page_calls, 1)
        self.assertEqual(len(owned.goto_calls), 1)
        self.assertTrue(owned.close_while_live)
        serialized = json.dumps(receipt)
        self.assertNotIn("private query phrase", serialized)
        self.assertNotIn("owned-target-secret", serialized)

    def test_receipt_separates_busy_retry_attempted_and_completed_counts(self):
        session = LeasePlaywright()
        status, receipt = self.run_lifecycle(
            session,
            post_click_outcome=oatd.PostClickOutcome(
                "busy_retry_navigation_failed", None, 2, 1, 1, 0
            ),
        )
        self.assertEqual(status, 1)
        self.assertEqual(receipt["submission"]["busy_retries_attempted"], 1)
        self.assertEqual(receipt["submission"]["busy_retries_completed"], 0)
        self.assertEqual(receipt["submission"]["busy_retries_performed"], 1)

    def test_non_distinct_new_page_is_never_closed_as_if_owned(self):
        session = LeasePlaywright()

        async def reused_baseline():
            return session.context.baselines[0]

        session.context.new_page = reused_baseline
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(receipt["result"]["classification"], "owned_page_not_distinct")
        self.assertEqual(session.context.baselines[0].close_calls, 0)
        self.assertFalse(session.context.baselines[0].is_closed())

    def test_alias_wrapper_for_a_baseline_target_fails_before_home_navigation(self):
        session = LeasePlaywright()

        async def alias_wrapper():
            alias = LeasePage(session.context, session.context.baselines[0].target_id)
            session.context.created = alias
            session.context.pages.append(alias)
            return alias

        session.context.new_page = alias_wrapper
        status, receipt = self.run_lifecycle(session)
        alias = session.context.created
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "owned_target_not_verified"
        )
        self.assertEqual(alias.goto_calls, [])
        self.assertEqual(alias.close_calls, 0)
        self.assertEqual(session.context.baselines[0].close_calls, 0)

    def test_new_wrapper_with_a_baseline_target_id_fails_before_navigation(self):
        session = LeasePlaywright()

        async def same_id_page():
            page = LeasePage(session.context, session.context.baselines[0].target_id)
            session.context.created = page
            return page

        session.context.new_page = same_id_page
        status, receipt = self.run_lifecycle(session)
        page = session.context.created
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "owned_target_not_verified"
        )
        self.assertEqual(page.goto_calls, [])
        self.assertEqual(page.close_calls, 0)

    def test_cleanup_failure_after_close_error_is_terminal_and_null(self):
        session = LeasePlaywright(close_raises=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertIsNone(receipt["result"]["source_reported_total"])
        self.assertFalse(receipt["result"]["observations_accepted"])
        self.assertTrue(session.context.created.close_while_live)
        self.assertNotIn("offline close failure", json.dumps(receipt))

    def test_closed_page_with_surviving_exact_target_is_terminal(self):
        session = LeasePlaywright(retain_closed_target=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["ownership"]["owned_target_disappeared"])
        self.assertFalse(receipt["ownership"]["baseline_target_set_preserved"])

    def test_baseline_mutation_is_detected_without_closing_a_baseline(self):
        session = LeasePlaywright(mutate_baseline_on_owned_close=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["ownership"]["baseline_pages_preserved"])
        self.assertFalse(receipt["ownership"]["baseline_target_set_preserved"])
        self.assertFalse(session.context.baselines[0].is_closed())

    def test_pre_submit_terminal_state_still_closes_owned_page_live(self):
        session = LeasePlaywright()
        status, receipt = self.run_lifecycle(
            session, inspection=valid_inspection("challenge")
        )
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "challenge_before_submission"
        )
        self.assertTrue(receipt["ownership"]["owned_target_disappeared"])
        self.assertTrue(session.context.created.close_while_live)


class OATDInputAndPrivacyTests(unittest.TestCase):
    def test_dry_run_does_not_instantiate_playwright(self):
        with tempfile.TemporaryDirectory() as directory:
            cfg = config(Path(directory), execute=False)
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("dry run must not start Playwright")

            status, receipt = asyncio.run(
                oatd.run_probe(cfg, playwright_factory=forbidden_factory)
            )
            self.assertEqual(status, 0)
            self.assertFalse(called)
            self.assertEqual(receipt["result"]["classification"], "dry_run")

    def test_direct_runtime_config_rejects_invalid_and_wrong_port_before_factory(self):
        with tempfile.TemporaryDirectory() as directory:
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("invalid config must not start Playwright")

            bad_configs = (
                oatd.ProbeConfig(
                    execute=True,
                    cdp_url="http://127.0.0.1:9223",
                    query="private query phrase",
                    field_label="Title",
                    timeout_seconds=1.0,
                    poll_interval_seconds=0.1,
                    busy_retries=0,
                    busy_retry_delay_seconds=1.0,
                    output_path=Path(directory) / "wrong-port.json",
                ),
                oatd.ProbeConfig(
                    execute="yes",
                    cdp_url=oatd.DEFAULT_CDP_URL,
                    query="private query phrase",
                    field_label="Title",
                    timeout_seconds=1.0,
                    poll_interval_seconds=0.1,
                    busy_retries=0,
                    busy_retry_delay_seconds=1.0,
                    output_path=Path(directory) / "invalid-execute.json",
                ),
            )
            for bad_config in bad_configs:
                with self.subTest(config=bad_config.cdp_url):
                    status, receipt = asyncio.run(
                        oatd.run_probe(bad_config, playwright_factory=forbidden_factory)
                    )
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        receipt["result"]["classification"], "invalid_runtime_config"
                    )
            self.assertFalse(called)

    def test_invalid_endpoint_and_output_collision_fail_before_browser_use(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.json"
            output.write_text("already here", encoding="utf-8")
            with self.assertRaises(SystemExit):
                oatd.parse_args(
                    [
                        "--query",
                        "x",
                        "--field-label",
                        "Title",
                        "--cdp-url",
                        "http://example.org:9222",
                        "--output-path",
                        str(Path(directory) / "new.json"),
                    ]
                )
            with self.assertRaises(SystemExit):
                oatd.parse_args(
                    [
                        "--query",
                        "x",
                        "--field-label",
                        "Title",
                        "--output-path",
                        str(output),
                    ]
                )
            with self.assertRaises(SystemExit):
                oatd.parse_args(
                    [
                        "--query",
                        "   ",
                        "--field-label",
                        "Title",
                        "--output-path",
                        str(Path(directory) / "blank.json"),
                    ]
                )

    def test_receipt_and_create_only_writer_do_not_leak_sensitive_values(self):
        receipt = oatd.new_receipt(True)
        encoded = json.dumps(receipt)
        for forbidden in (
            "private query phrase",
            "owned-target-secret",
            "https://private.example/",
            "offline close failure",
        ):
            self.assertNotIn(forbidden, encoded)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            oatd.write_new_json(path, receipt)
            with self.assertRaises(FileExistsError):
                oatd.write_new_json(path, receipt)

    def test_failed_create_only_write_never_deletes_a_concurrent_winner(self):
        receipt = oatd.new_receipt(False)
        winner = b"concurrent winner"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"

            class FailingWriter:
                def __enter__(self):
                    return self

                def write(self, _data):
                    path.unlink()
                    path.write_bytes(winner)
                    raise OSError("offline write failure")

                def __exit__(self, _type, _value, _traceback):
                    os.close(descriptor)
                    return False

            descriptor = -1

            def fake_fdopen(fd, *_args, **_kwargs):
                nonlocal descriptor
                descriptor = fd
                return FailingWriter()

            with mock.patch.object(oatd.os, "fdopen", side_effect=fake_fdopen):
                with self.assertRaises(OSError):
                    oatd.write_new_json(path, receipt)
            self.assertEqual(path.read_bytes(), winner)


if __name__ == "__main__":
    unittest.main()
