"""Offline invariants for the IEEE Xplore Language-control probe."""

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


def load_probe():
    name = "ieee_language_control_probe_offline_test"
    spec = importlib.util.spec_from_file_location(
        name, SCRIPTS / "ieee_language_control_probe.py"
    )
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError("could not load language probe")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


probe = load_probe()


def projection_payload(**overrides):
    payload = {
        "ready": True,
        "expected_route": True,
        "challenge_detected": False,
        "access_detected": False,
        "login_detected": False,
        "source_error_detected": False,
        "busy_detected": False,
        "language": {
            "language_facet_count": 1,
            "language_option_count": 2,
            "english_option_count": 1,
            "apply_control_count": 1,
            "selected_option_count": 0,
        },
    }
    payload.update(overrides)
    return payload


class FakeClock:
    def __init__(self):
        self.value = 0.0
        self.sleeps = []

    def __call__(self):
        return self.value

    async def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.value += seconds


class ProjectionPage:
    def __init__(self, values):
        self.values = list(values)
        self.evaluate_calls = 0

    async def evaluate(self, *_args):
        self.evaluate_calls += 1
        value = self.values.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


class LanguageProjectionTests(unittest.TestCase):
    def test_projection_is_allowlisted_and_receipt_has_no_source_text(self):
        inventory = probe.projection_from_payload(projection_payload())
        self.assertEqual(inventory.language_facet_count, 1)
        self.assertEqual(inventory.english_option_count, 1)
        receipt = probe.new_receipt(True)
        probe._record_language_projection(receipt, inventory)
        encoded = json.dumps(receipt)
        self.assertNotIn("English", encoded)
        self.assertNotIn("nanosatellite", encoded)
        self.assertNotIn("private source text", encoded)
        self.assertNotIn('"body_text":', encoded)
        self.assertFalse(receipt["language"]["language_selection_attempted"])
        self.assertFalse(receipt["language"]["english_limit_applied"])

    def test_inventory_requires_one_unselected_english_option(self):
        healthy, accepted = probe.classify_inventory(
            probe.projection_from_payload(projection_payload())
        )
        self.assertEqual(healthy, "language_control_inventory_healthy")
        self.assertTrue(accepted)

        cases = (
            ({"language_facet_count": 0}, "language_facet_not_present"),
            ({"language_facet_count": 2}, "language_facet_ambiguous"),
            ({"english_option_count": 0}, "english_option_not_verified"),
            ({"selected_option_count": 1}, "inherited_language_selection_detected"),
            ({"busy_detected": True}, "busy_detected"),
            ({"challenge_detected": True}, "challenge_detected"),
        )
        for changes, expected in cases:
            with self.subTest(expected=expected):
                payload = projection_payload()
                language_changes = {
                    key: value
                    for key, value in changes.items()
                    if key in payload["language"]
                }
                payload["language"].update(language_changes)
                payload.update(
                    {
                        key: value
                        for key, value in changes.items()
                        if key not in payload["language"]
                    }
                )
                classification, accepted = probe.classify_inventory(
                    probe.projection_from_payload(payload)
                )
                self.assertEqual(classification, expected)
                self.assertFalse(accepted)

    def test_projection_rejects_malformed_or_raw_payload(self):
        with self.assertRaises(probe.ProbeFailure):
            probe.projection_from_payload({"body_text": "private source text"})
        malformed = projection_payload()
        malformed["language"]["language_option_count"] = -1
        with self.assertRaises(probe.ProbeFailure):
            probe.projection_from_payload(malformed)

    def test_passive_projection_retries_only_context_replacement(self):
        page = ProjectionPage(
            [
                RuntimeError("Execution context was destroyed"),
                projection_payload(),
            ]
        )
        clock = FakeClock()
        outcome = asyncio.run(
            probe.wait_for_language_inventory(
                page,
                timeout_seconds=1.0,
                poll_interval_seconds=0.1,
                clock=clock,
                sleeper=clock.sleep,
            )
        )
        self.assertIsNotNone(outcome.inventory)
        self.assertEqual(outcome.attempts, 2)
        self.assertIsNone(outcome.failure_code)
        self.assertEqual(clock.sleeps, [0.1])

    def test_busy_is_terminal_without_a_second_projection_or_navigation(self):
        page = ProjectionPage([projection_payload(busy_detected=True)])
        outcome = asyncio.run(
            probe.wait_for_language_inventory(
                page,
                timeout_seconds=1.0,
                poll_interval_seconds=0.1,
            )
        )
        self.assertEqual(outcome.attempts, 1)
        self.assertTrue(outcome.inventory.busy_detected)
        self.assertEqual(page.evaluate_calls, 1)


class ConfigurationAndOutputTests(unittest.TestCase):
    def config(self, path, **overrides):
        values = {
            "execute": False,
            "query": '("All Metadata":"nanosatellite")',
            "year_start": 2011,
            "year_end": 2026,
            "content_types": ("Journals", "Conferences"),
            "cdp_url": probe.DEFAULT_CDP_URL,
            "timeout_seconds": 1.0,
            "poll_interval_seconds": 0.1,
            "output_path": path,
        }
        values.update(overrides)
        return probe.ProbeConfig(**values)

    def test_endpoint_is_exact_and_no_fresh_browser_mode_exists(self):
        with self.assertRaises(probe.InputValidationError):
            probe.validate_loopback_cdp_url("http://localhost:9222")
        with self.assertRaises(probe.InputValidationError):
            probe.validate_loopback_cdp_url("http://127.0.0.1:9230")
        parser = probe.build_parser()
        self.assertNotIn("--fresh-browser", parser.format_help())
        args = parser.parse_args(
            [
                "--query",
                "q",
                "--year-start",
                "2011",
                "--year-end",
                "2026",
                "--content-type",
                "Journals",
                "--output-path",
                "/tmp/language-probe.json",
            ]
        )
        self.assertEqual(args.cdp_url, probe.DEFAULT_CDP_URL)

    def test_dry_run_is_create_only_and_diagnostic_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            status, receipt = asyncio.run(
                probe.run_probe(self.config(output))
            )
            self.assertEqual(status, 0)
            self.assertEqual(receipt["result"]["classification"], "dry_run")
            self.assertTrue(receipt["diagnostic_only"])
            self.assertFalse(receipt["screening_performed"])
            self.assertFalse(receipt["candidate_import_permitted"])
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["result"], receipt["result"])
            self.assertNotIn("nanosatellite", json.dumps(saved))

            original = output.read_bytes()
            status, second = asyncio.run(probe.run_probe(self.config(output)))
            self.assertEqual(status, 1)
            self.assertEqual(second["result"]["classification"], "invalid_runtime_config")
            self.assertEqual(output.read_bytes(), original)

    def test_invalid_runtime_configuration_does_not_write_source_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            status, receipt = asyncio.run(
                probe.run_probe(
                    self.config(output, cdp_url="http://localhost:9222")
                )
            )
            self.assertEqual(status, 1)
            self.assertEqual(receipt["result"]["classification"], "invalid_runtime_config")
            self.assertFalse(output.exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
