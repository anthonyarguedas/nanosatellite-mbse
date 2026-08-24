"""Deterministic offline tests for the Engineering Village route probe."""

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
from types import SimpleNamespace


SCRIPTS = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:  # pragma: no cover - test setup
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ev = load_module(
    "test_engineering_village_route_probe_module", "engineering_village_route_probe.py"
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


def projection_payload(
    *,
    title: bool = True,
    access: bool = False,
    login: bool = False,
    challenge: bool = False,
    syntax: bool = False,
    compendex_present: bool = True,
    compendex_checked: bool | None = True,
    inspec_present: bool = True,
    inspec_checked: bool | None = True,
    query: bool = True,
) -> dict:
    controls = {
        "compendex": {"present": compendex_present, "checked": compendex_checked},
        "inspec": {"present": inspec_present, "checked": inspec_checked},
        "all": {"present": True, "checked": False},
        "knovel": {"present": True, "checked": False},
        "autostemming": {"present": True, "checked": False},
        "relevance": {"present": True, "checked": True},
    }
    return {
        "expected_expert_title": title,
        "access_detected": access,
        "login_detected": login,
        "challenge_detected": challenge,
        "syntax_detected": syntax,
        "controls": controls,
        "query_field_present": query,
    }


class ProjectionPage:
    """A projection-only no-network page double."""

    def __init__(self, evaluations: list[object], url: str | None = None) -> None:
        self.evaluations = list(evaluations)
        self.url = url or ev.PUBLIC_PAIRED_EXPERT_ROUTE
        self.goto_calls: list[tuple[object, dict]] = []

    async def evaluate(self, *_args, **_kwargs):
        if not self.evaluations:
            raise AssertionError("unexpected projection")
        value = self.evaluations.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    async def goto(self, *args, **kwargs):
        self.goto_calls.append((args, kwargs))


class TargetSession:
    def __init__(
        self, browser: "LeaseBrowser", page: "LeasePage | None" = None
    ) -> None:
        self.browser = browser
        self.page = page

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
        return None


class LeasePage:
    def __init__(
        self,
        context: "LeaseContext",
        target_id: str,
        *,
        evaluations: list[object] | None = None,
        close_raises: bool = False,
    ) -> None:
        self.context = context
        self.target_id = target_id
        self.evaluations = list(evaluations or [])
        self.close_raises = close_raises
        self.closed = False
        self.close_while_live: bool | None = None
        self.close_calls = 0
        self.goto_calls: list[tuple[object, dict]] = []
        self.url = ev.PUBLIC_PAIRED_EXPERT_ROUTE

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

    async def goto(self, *args, **kwargs):
        self.goto_calls.append((args, kwargs))
        return SimpleNamespace(status=200)

    async def evaluate(self, *_args, **_kwargs):
        if not self.evaluations:
            raise AssertionError("unexpected lease projection")
        value = self.evaluations.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


class LeaseContext:
    def __init__(
        self,
        session: "LeasePlaywright",
        *,
        baseline_count: int = 2,
        close_raises: bool = False,
        mutate_baseline_on_owned_close: bool = False,
        evaluations: list[object] | None = None,
    ) -> None:
        self.session = session
        self.close_raises = close_raises
        self.mutate_baseline_on_owned_close = mutate_baseline_on_owned_close
        self.evaluations = evaluations or [projection_payload(), projection_payload()]
        self.baselines = [
            LeasePage(self, f"baseline-{number}") for number in range(baseline_count)
        ]
        self.pages = list(self.baselines)
        self.created: LeasePage | None = None
        self.new_page_calls = 0

    async def new_page(self) -> LeasePage:
        self.new_page_calls += 1
        self.created = LeasePage(
            self,
            "owned-target-secret",
            evaluations=self.evaluations,
            close_raises=self.close_raises,
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
        baseline_count: int = 2,
        close_raises: bool = False,
        retain_closed_target: bool = False,
        mutate_baseline_on_owned_close: bool = False,
        evaluations: list[object] | None = None,
    ) -> None:
        self.live = False
        self.context = LeaseContext(
            self,
            baseline_count=baseline_count,
            close_raises=close_raises,
            mutate_baseline_on_owned_close=mutate_baseline_on_owned_close,
            evaluations=evaluations,
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


def config(tmp: Path, *, execute: bool = True):
    return ev.ProbeConfig(
        execute=execute,
        cdp_url="http://127.0.0.1:9222",
        timeout_seconds=1.0,
        stabilization_interval_seconds=0.1,
        output_path=tmp / "receipt.json",
    )


class EngineeringVillageRouteClassificationTests(unittest.TestCase):
    def test_python_route_classification_never_returns_the_input_url(self):
        public = ev.classify_public_paired_expert_url(ev.PUBLIC_PAIRED_EXPERT_ROUTE)
        nonpublic = ev.classify_public_paired_expert_url(
            "https://www.engineeringvillage.com/search/expert.url?database=3&session=private"
        )
        other = ev.classify_public_paired_expert_url(
            "https://elsewhere.example/search/expert.url"
        )
        malformed = ev.classify_public_paired_expert_url(
            "https://www.engineeringvillage.com:bad/"
        )
        self.assertEqual(public.route_class, "public_paired_expert_route")
        self.assertTrue(public.expected_host)
        self.assertTrue(public.expected_path)
        self.assertTrue(public.public_paired_expert_route)
        self.assertEqual(
            nonpublic.route_class, "expected_expert_route_nonpublic_or_unpaired"
        )
        self.assertFalse(nonpublic.public_paired_expert_route)
        self.assertEqual(other.route_class, "off_expected_host")
        self.assertEqual(malformed.route_class, "invalid_url")
        self.assertNotIn("session=private", repr(nonpublic))

    def test_only_fixed_browser_failure_subclasses_are_retriable(self):
        context = ev.classify_projection_exception(
            RuntimeError(
                "Execution context was destroyed, most likely because of a navigation"
            )
        )
        navigation = ev.classify_projection_exception(
            RuntimeError("navigation is in progress")
        )
        durable = ev.classify_projection_exception(
            RuntimeError("arbitrary browser fault")
        )
        self.assertIsInstance(context, ev.ExecutionContextReplaced)
        self.assertIsInstance(navigation, ev.OngoingNavigation)
        self.assertIsInstance(durable, ev.DurableProjectionFailure)
        self.assertEqual(context.code, "projection_execution_context_replaced")
        self.assertEqual(navigation.code, "projection_ongoing_navigation")

    def test_safe_marker_and_paired_control_classification_is_distinct(self):
        cases = (
            ({"challenge": True}, "challenge_detected"),
            ({"access": True}, "access_detected"),
            ({"login": True}, "login_detected"),
            ({"syntax": True}, "syntax_detected"),
            ({"compendex_checked": False}, "paired_controls_not_checked"),
            ({"query": False}, "query_field_not_present"),
        )
        route = ev.classify_public_paired_expert_url(ev.PUBLIC_PAIRED_EXPERT_ROUTE)
        for kwargs, expected in cases:
            with self.subTest(expected=expected):
                sample = ev.ProjectionSample(
                    route=route,
                    projection=ev.projection_from_payload(projection_payload(**kwargs)),
                )
                outcome = ev.StabilizationOutcome(sample, 2, 2, None, False)
                receipt = ev.new_receipt(True)
                receipt["navigation"]["response_status"] = 200
                ev._apply_stabilization(receipt, outcome)
                classification, healthy = ev.classify_route_result(receipt, outcome)
                self.assertEqual(classification, expected)
                self.assertFalse(healthy)


class EngineeringVillageStabilizationTests(unittest.TestCase):
    def stabilize(self, page: ProjectionPage, *, timeout: float = 1.0):
        clock = FakeClock()
        outcome = asyncio.run(
            ev.stabilize_after_domcontentloaded(
                page,
                timeout_seconds=timeout,
                interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        return outcome, clock

    def test_execution_context_replacement_is_passively_retried_then_stabilized(self):
        page = ProjectionPage(
            [
                RuntimeError("Execution context was destroyed"),
                projection_payload(),
                projection_payload(),
            ]
        )
        outcome, clock = self.stabilize(page)
        self.assertIsNotNone(outcome.sample)
        self.assertEqual(outcome.attempts, 3)
        self.assertEqual(outcome.stable_samples, 2)
        self.assertIsNone(outcome.failure_code)
        self.assertEqual(clock.sleeps, [0.1, 0.1])
        self.assertEqual(page.goto_calls, [])

    def test_ongoing_navigation_retries_but_durable_projection_does_not(self):
        page = ProjectionPage(
            [RuntimeError("navigation is in progress"), RuntimeError("other failure")]
        )
        outcome, clock = self.stabilize(page)
        self.assertIsNone(outcome.sample)
        self.assertEqual(outcome.failure_code, "projection_durable_failure")
        self.assertFalse(outcome.timed_out)
        self.assertEqual(outcome.attempts, 2)
        self.assertEqual(clock.sleeps, [0.1])

    def test_persistent_transient_failure_has_a_finite_fixed_class_timeout(self):
        page = ProjectionPage([RuntimeError("Execution context was destroyed")] * 10)
        outcome, clock = self.stabilize(page, timeout=0.2)
        self.assertIsNone(outcome.sample)
        self.assertEqual(outcome.failure_code, "projection_execution_context_replaced")
        self.assertTrue(outcome.timed_out)
        self.assertGreaterEqual(outcome.attempts, 2)
        self.assertLessEqual(sum(clock.sleeps), 0.2)

    def test_invalid_allowlisted_projection_is_durable(self):
        invalid = projection_payload()
        invalid["controls"] = {"compendex": {"present": True, "checked": True}}
        outcome, _ = self.stabilize(ProjectionPage([invalid]))
        self.assertEqual(outcome.failure_code, "projection_durable_failure")
        self.assertFalse(outcome.timed_out)

    def test_late_equal_projection_is_not_accepted_as_stable(self):
        clock = FakeClock()

        class LatePage(ProjectionPage):
            def __init__(self):
                super().__init__([])
                self.calls = 0

            async def evaluate(self, *_args, **_kwargs):
                self.calls += 1
                if self.calls == 2:
                    clock.value = 1.0
                return projection_payload()

        page = LatePage()
        outcome = asyncio.run(
            ev.stabilize_after_domcontentloaded(
                page,
                timeout_seconds=1.0,
                interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertIsNone(outcome.sample)
        self.assertEqual(outcome.failure_code, "projection_stabilization_timeout")
        self.assertTrue(outcome.timed_out)
        self.assertEqual(outcome.stable_samples, 0)
        self.assertEqual(page.calls, 2)

    def test_slow_projection_is_bounded_by_the_remaining_deadline(self):
        class SlowPage(ProjectionPage):
            async def evaluate(self, *_args, **_kwargs):
                await asyncio.sleep(0.05)
                return projection_payload()

        outcome = asyncio.run(
            ev.stabilize_after_domcontentloaded(
                SlowPage([]), timeout_seconds=0.01, interval_seconds=0.01
            )
        )
        self.assertIsNone(outcome.sample)
        self.assertEqual(outcome.failure_code, "projection_stabilization_timeout")
        self.assertTrue(outcome.timed_out)


class EngineeringVillageOwnershipAndCleanupTests(unittest.TestCase):
    def run_lifecycle(self, session: LeasePlaywright):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            return asyncio.run(
                ev.run_probe(
                    config(Path(directory)),
                    playwright_factory=lambda: session,
                    clock=clock,
                    sleeper=clock.sleep,
                )
            )

    def test_one_owned_page_one_navigation_preserves_every_baseline(self):
        session = LeasePlaywright(baseline_count=3)
        status, receipt = self.run_lifecycle(session)
        owned = session.context.created
        self.assertEqual(status, 0)
        self.assertTrue(receipt["result"]["healthy"])
        self.assertEqual(receipt["navigation_attempt_count"], 1)
        self.assertEqual(len(owned.goto_calls), 1)
        self.assertEqual(session.context.new_page_calls, 1)
        self.assertEqual(session.context.pages, session.context.baselines)
        self.assertTrue(receipt["ownership"]["baseline_pages_preserved"])
        self.assertTrue(receipt["ownership"]["owned_target_disappeared"])
        self.assertTrue(owned.close_while_live)
        serialized = json.dumps(receipt)
        self.assertNotIn("owned-target-secret", serialized)
        self.assertNotIn("session=private", serialized)

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

    def test_alias_wrapper_for_a_baseline_target_fails_before_navigation(self):
        session = LeasePlaywright()

        async def alias_wrapper():
            alias = LeasePage(
                session.context,
                session.context.baselines[0].target_id,
                evaluations=session.context.evaluations,
            )
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
            page = LeasePage(
                session.context,
                session.context.baselines[0].target_id,
                evaluations=session.context.evaluations,
            )
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

    def test_close_failure_is_terminal_and_no_route_observation_is_accepted(self):
        session = LeasePlaywright(close_raises=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["result"]["observations_accepted"])
        self.assertTrue(session.context.created.close_while_live)
        self.assertNotIn("offline close failure", json.dumps(receipt))

    def test_surviving_owned_target_after_close_is_terminal(self):
        session = LeasePlaywright(retain_closed_target=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["ownership"]["owned_target_disappeared"])
        self.assertFalse(receipt["ownership"]["baseline_target_set_preserved"])

    def test_baseline_change_is_detected_without_closing_baseline_pages(self):
        session = LeasePlaywright(mutate_baseline_on_owned_close=True)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["ownership"]["baseline_pages_preserved"])
        self.assertFalse(receipt["ownership"]["baseline_target_set_preserved"])
        self.assertFalse(session.context.baselines[0].is_closed())

    def test_two_existing_contexts_are_rejected_before_owned_page_creation(self):
        session = LeasePlaywright()
        session.browser.contexts.append(session.context)
        status, receipt = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "unexpected_browser_context_count"
        )
        self.assertIsNone(session.context.created)


class EngineeringVillageInputAndPrivacyTests(unittest.TestCase):
    def test_dry_run_does_not_start_playwright(self):
        with tempfile.TemporaryDirectory() as directory:
            cfg = config(Path(directory), execute=False)
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("dry run must not start Playwright")

            status, receipt = asyncio.run(
                ev.run_probe(cfg, playwright_factory=forbidden_factory)
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
                ev.ProbeConfig(
                    execute=True,
                    cdp_url="http://127.0.0.1:9223",
                    timeout_seconds=1.0,
                    stabilization_interval_seconds=0.1,
                    output_path=Path(directory) / "wrong-port.json",
                ),
                ev.ProbeConfig(
                    execute="yes",
                    cdp_url=ev.DEFAULT_CDP_URL,
                    timeout_seconds=1.0,
                    stabilization_interval_seconds=0.1,
                    output_path=Path(directory) / "invalid-execute.json",
                ),
            )
            for bad_config in bad_configs:
                with self.subTest(config=bad_config.cdp_url):
                    status, receipt = asyncio.run(
                        ev.run_probe(bad_config, playwright_factory=forbidden_factory)
                    )
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        receipt["result"]["classification"], "invalid_runtime_config"
                    )
            self.assertFalse(called)

    def test_invalid_inputs_and_output_collision_fail_before_source_action(self):
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "existing.json"
            existing.write_text("x", encoding="utf-8")
            cases = [
                [
                    "--cdp-url",
                    "http://remote.example:9222",
                    "--output-path",
                    str(Path(directory) / "remote.json"),
                ],
                [
                    "--timeout-seconds",
                    "nan",
                    "--output-path",
                    str(Path(directory) / "nan.json"),
                ],
                ["--output-path", str(existing)],
            ]
            for argv in cases:
                with self.subTest(argv=argv), self.assertRaises(SystemExit):
                    ev.parse_args(argv)

    def test_create_only_output_and_receipt_privacy(self):
        receipt = ev.new_receipt(True)
        encoded = json.dumps(receipt)
        for forbidden in (
            "owned-target-secret",
            "session=private",
            "https://private.example/",
            "offline close failure",
        ):
            self.assertNotIn(forbidden, encoded)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            ev.write_new_json(path, receipt)
            with self.assertRaises(FileExistsError):
                ev.write_new_json(path, receipt)

    def test_failed_create_only_write_never_deletes_a_concurrent_winner(self):
        receipt = ev.new_receipt(False)
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

            with mock.patch.object(ev.os, "fdopen", side_effect=fake_fdopen):
                with self.assertRaises(OSError):
                    ev.write_new_json(path, receipt)
            self.assertEqual(path.read_bytes(), winner)

    def test_source_has_one_navigation_and_no_reload_fallback(self):
        source = (SCRIPTS / "engineering_village_route_probe.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(source.count(".goto("), 1)
        self.assertNotIn(".reload(", source)


if __name__ == "__main__":
    unittest.main()
