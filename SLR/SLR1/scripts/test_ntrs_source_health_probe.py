"""Offline tests for the record-free NTRS source-health precheck."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPTS = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    if spec is None or spec.loader is None:  # pragma: no cover - test setup guard
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


probe = load_module(
    "test_ntrs_source_health_probe_module", "ntrs_source_health_probe.py"
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


def projection_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sourceIdentity": True,
        "searchControlPresent": True,
        "challengeDetected": False,
        "accessDetected": False,
        "loginDetected": False,
        "busyDetected": False,
        "errorDetected": False,
        "documentAvailable": True,
        "documentReadyState": "complete",
    }
    payload.update(overrides)
    return payload


class ProjectionPage:
    def __init__(self, evaluations: list[object], url: str = probe.SOURCE_ROOT_URL):
        self.evaluations = list(evaluations)
        self.url = url
        self.goto_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    async def evaluate(self, script: str, *_args: object):
        if script != probe.NTRS_HEALTH_PROJECTION_SCRIPT:
            raise AssertionError("unexpected projection script")
        if not self.evaluations:
            raise AssertionError("unexpected projection")
        value = self.evaluations.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    async def goto(self, *args: object, **kwargs: object):
        self.goto_calls.append((args, kwargs))
        return SimpleNamespace(status=200)


class LeasePage:
    def __init__(
        self,
        context: "LeaseContext",
        *,
        baseline: bool = False,
        evaluations: list[object] | None = None,
        close_raises: bool = False,
    ) -> None:
        self.context = context
        self.baseline = baseline
        self.evaluations = list(evaluations or [])
        self.close_raises = close_raises
        self.closed = False
        self.close_while_live: bool | None = None
        self.goto_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.url = probe.SOURCE_ROOT_URL

    def is_closed(self) -> bool:
        return self.closed

    async def close(self) -> None:
        self.close_while_live = self.context.session.live
        if self.close_raises:
            raise RuntimeError("offline close failure")
        self.closed = True
        if self in self.context.pages:
            self.context.pages.remove(self)

    async def goto(self, *args: object, **kwargs: object):
        self.goto_calls.append((args, kwargs))
        return SimpleNamespace(status=200)

    async def evaluate(self, script: str, *_args: object):
        if script != probe.NTRS_HEALTH_PROJECTION_SCRIPT:
            raise AssertionError("unexpected health script")
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
        evaluations: list[object] | None = None,
        close_raises: bool = False,
        baseline_count: int = 1,
    ) -> None:
        self.session = session
        self.evaluations = list(evaluations or [])
        self.close_raises = close_raises
        self.baselines = [
            LeasePage(self, baseline=True) for _ in range(baseline_count)
        ]
        self.pages = list(self.baselines)
        self.created: LeasePage | None = None

    async def new_page(self) -> LeasePage:
        self.created = LeasePage(
            self,
            evaluations=self.evaluations,
            close_raises=self.close_raises,
        )
        self.pages.append(self.created)
        return self.created


class LeaseBrowser:
    def __init__(self, context: LeaseContext, context_count: int = 1) -> None:
        self.context = context
        self.contexts = [context] * context_count


class LeaseChromium:
    def __init__(self, session: "LeasePlaywright") -> None:
        self.session = session
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def connect_over_cdp(self, endpoint: str, **kwargs: object) -> LeaseBrowser:
        if not self.session.live:
            raise AssertionError("CDP attach must happen inside Playwright")
        self.calls.append((endpoint, kwargs))
        return self.session.browser


class LeasePlaywright:
    def __init__(
        self,
        *,
        evaluations: list[object] | None = None,
        close_raises: bool = False,
        context_count: int = 1,
        baseline_count: int = 1,
    ) -> None:
        self.live = False
        self.context = LeaseContext(
            self,
            evaluations=evaluations,
            close_raises=close_raises,
            baseline_count=baseline_count,
        )
        self.browser = LeaseBrowser(self.context, context_count=context_count)
        self.chromium = LeaseChromium(self)

    async def __aenter__(self):
        self.live = True
        return self

    async def __aexit__(self, *_args: object):
        self.live = False
        return False


def config(directory: Path, *, execute: bool = True, timeout: float = 1.0):
    return probe.ProbeConfig(
        execute=execute,
        cdp_url=probe.DEFAULT_CDP_URL,
        timeout_seconds=timeout,
        stabilization_interval_seconds=min(0.1, timeout),
        output_path=directory / "health.json",
    )


class NTRSHealthProjectionTests(unittest.TestCase):
    def test_route_classification_is_strict_and_does_not_return_urls(self):
        normal = probe.classify_ntrs_url("https://ntrs.nasa.gov/")
        search = probe.classify_ntrs_url("https://www.ntrs.nasa.gov/search")
        query = probe.classify_ntrs_url("https://ntrs.nasa.gov/search?q=secret")
        other = probe.classify_ntrs_url("https://example.invalid/")
        self.assertTrue(normal.normal_source_route)
        self.assertTrue(search.normal_source_route)
        self.assertFalse(query.normal_source_route)
        self.assertEqual(other.route_class, "off_source_route")
        self.assertNotIn("secret", repr(query))

    def test_projection_accepts_only_the_fixed_boolean_enum_allowlist(self):
        route = probe.classify_ntrs_url(probe.SOURCE_ROOT_URL)
        parsed = probe.projection_from_payload(projection_payload(), route)
        self.assertEqual(parsed.route_class, "normal_source_route")
        self.assertTrue(parsed.search_control_present)
        malformed = projection_payload(documentReadyState="raw page text")
        with self.assertRaises(probe.ProjectionFailure):
            probe.projection_from_payload(malformed, route)

    def test_stabilization_requires_two_equal_samples_for_health(self):
        clock = FakeClock()
        page = ProjectionPage([projection_payload(), projection_payload()])
        outcome = asyncio.run(
            probe.stabilize_health(
                page,
                timeout_seconds=1.0,
                interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(outcome.stable_samples, 2)
        self.assertIsNone(outcome.failure_code)
        self.assertEqual(clock.sleeps, [0.1])

    def test_challenge_is_terminal_and_never_passively_retried(self):
        clock = FakeClock()
        page = ProjectionPage([projection_payload(challengeDetected=True)])
        outcome = asyncio.run(
            probe.stabilize_health(
                page,
                timeout_seconds=1.0,
                interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(outcome.stable_samples, 1)
        self.assertEqual(page.evaluations, [])
        self.assertFalse(outcome.timed_out)

    def test_known_transient_projection_failure_is_bounded_then_recovered(self):
        clock = FakeClock()
        page = ProjectionPage(
            [
                RuntimeError("Execution context was destroyed"),
                projection_payload(),
                projection_payload(),
            ]
        )
        outcome = asyncio.run(
            probe.stabilize_health(
                page,
                timeout_seconds=1.0,
                interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertEqual(outcome.stable_samples, 2)
        self.assertEqual(outcome.attempts, 3)
        self.assertEqual(clock.sleeps, [0.1, 0.1])

    def test_static_guard_has_no_api_fetch_or_navigation_fallback(self):
        source = (SCRIPTS / "ntrs_source_health_probe.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("/api/citations/search", source)
        self.assertNotIn("import requests", source)
        self.assertNotRegex(source, r"(?i)fetch\s*\(")
        self.assertNotIn("request_context", source.casefold())
        self.assertNotIn(".reload(", source)
        self.assertEqual(source.count("owned_page.goto("), 1)


class NTRSHealthLifecycleTests(unittest.TestCase):
    def run_lifecycle(self, session: LeasePlaywright):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            status, receipt = asyncio.run(
                probe.run_probe(
                    config(Path(directory)),
                    playwright_factory=lambda: session,
                    clock=clock,
                    sleeper=clock.sleep,
                )
            )
            return status, receipt, session.context.created

    def test_healthy_precheck_is_record_free_and_closes_only_its_owned_page(self):
        payloads = [projection_payload(), projection_payload()]
        session = LeasePlaywright(evaluations=payloads, baseline_count=2)
        status, receipt, owned = self.run_lifecycle(session)
        self.assertEqual(status, 0)
        self.assertTrue(receipt["result"]["healthy"])
        self.assertEqual(receipt["navigation_attempt_count"], 1)
        self.assertEqual(receipt["records_observed"], 0)
        self.assertIsNone(receipt["source_total"])
        self.assertTrue(receipt["ownership"]["owned_page_closed"])
        self.assertTrue(receipt["ownership"]["owned_page_absent_after_close"])
        self.assertTrue(receipt["ownership"]["baseline_pages_preserved"])
        self.assertEqual(session.context.pages, session.context.baselines)
        self.assertTrue(owned.close_while_live)
        serialized = json.dumps(receipt)
        self.assertNotIn("https://ntrs.nasa.gov", serialized)
        self.assertNotIn("private", serialized)

    def test_busy_or_challenge_fails_closed_without_query_or_retry(self):
        session = LeasePlaywright(
            evaluations=[projection_payload(busyDetected=True)]
        )
        status, receipt, owned = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(receipt["result"]["classification"], "busy_detected")
        self.assertEqual(len(owned.goto_calls), 1)
        self.assertEqual(receipt["navigation"]["projection_attempts"], 1)
        self.assertTrue(receipt["ownership"]["owned_page_closed"])

    def test_cleanup_failure_invalidates_even_a_healthy_projection(self):
        session = LeasePlaywright(
            evaluations=[projection_payload(), projection_payload()],
            close_raises=True,
        )
        status, receipt, _ = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "cleanup_verification_failed"
        )
        self.assertFalse(receipt["result"]["observations_accepted"])
        self.assertFalse(receipt["ownership"]["owned_page_closed"])
        self.assertNotIn("offline close failure", json.dumps(receipt))

    def test_unverified_owned_page_is_not_closed_as_if_owned(self):
        session = LeasePlaywright(evaluations=[projection_payload()])

        async def unlisted_page():
            session.context.created = LeasePage(
                session.context, evaluations=[projection_payload()]
            )
            return session.context.created

        session.context.new_page = unlisted_page
        status, receipt, owned = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"], "owned_page_cleanup_handoff_required"
        )
        self.assertEqual(owned.close_while_live, None)
        self.assertEqual(session.context.pages, session.context.baselines)

    def test_multiple_contexts_stop_before_page_creation(self):
        session = LeasePlaywright(context_count=2)
        status, receipt, owned = self.run_lifecycle(session)
        self.assertEqual(status, 1)
        self.assertEqual(
            receipt["result"]["classification"],
            "unexpected_browser_context_count",
        )
        self.assertIsNone(owned)


class NTRSHealthInputTests(unittest.TestCase):
    def test_dry_run_writes_no_source_receipt_and_never_starts_playwright(self):
        with tempfile.TemporaryDirectory() as directory:
            called = False

            def forbidden_factory():
                nonlocal called
                called = True
                raise AssertionError("dry run must not start Playwright")

            status, receipt = asyncio.run(
                probe.run_probe(
                    config(Path(directory), execute=False),
                    playwright_factory=forbidden_factory,
                )
            )
            self.assertEqual(status, 0)
            self.assertFalse(called)
            self.assertEqual(receipt["result"]["classification"], "dry_run")
            self.assertEqual(
                json.loads((Path(directory) / "health.json").read_text())[
                    "result"
                ]["status"],
                "not_run",
            )

    def test_invalid_endpoint_and_collision_block_browser_before_source_action(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.json"
            output.write_text("winner\n", encoding="utf-8")
            bad = probe.ProbeConfig(
                execute=True,
                cdp_url="http://127.0.0.1:9223",
                timeout_seconds=1.0,
                stabilization_interval_seconds=0.1,
                output_path=Path(directory) / "bad.json",
            )
            status, receipt = asyncio.run(
                probe.run_probe(
                    bad,
                    playwright_factory=lambda: (_ for _ in ()).throw(
                        AssertionError("must not start")
                    ),
                )
            )
            self.assertEqual(status, 1)
            self.assertEqual(
                receipt["result"]["classification"], "invalid_runtime_config"
            )
            collided = probe.ProbeConfig(
                execute=True,
                cdp_url=probe.DEFAULT_CDP_URL,
                timeout_seconds=1.0,
                stabilization_interval_seconds=0.1,
                output_path=output,
            )
            status, receipt = asyncio.run(
                probe.run_probe(
                    collided,
                    playwright_factory=lambda: (_ for _ in ()).throw(
                        AssertionError("must not start")
                    ),
                )
            )
            self.assertEqual(status, 1)
            self.assertEqual(
                receipt["result"]["classification"], "invalid_runtime_config"
            )
            self.assertEqual(output.read_text(encoding="utf-8"), "winner\n")

    def test_cli_help_is_offline(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "ntrs_source_health_probe.py"), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("--execute", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
