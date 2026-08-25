"""Offline tests for the bounded Engineering Village P03 paired event."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "test_engineering_village_paired_diagnostic_module",
    SCRIPTS / "engineering_village_paired_diagnostic.py",
)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - test setup
    raise RuntimeError("could not load paired diagnostic")
ev = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ev
SPEC.loader.exec_module(ev)


class EngineeringVillagePairedDiagnosticTests(unittest.TestCase):
    def make_config(
        self,
        directory: str,
        *,
        execute: bool = True,
        pilot_date: date = date(2026, 8, 25),
    ) -> tuple[ev.PairedDiagnosticConfig, Path, Path]:
        root = Path(directory)
        query = root / "B1.ev-expert.txt"
        query.write_text('("embedded systems") AND ("model-based systems engineering")\n', encoding="utf-8")
        output = root / "op-02-paired-diagnostic.json"
        config = ev.PairedDiagnosticConfig(
            execute=execute,
            attempt_id="S-D04-P03-20260825T002312-0400",
            cdp_url=ev.DEFAULT_CDP_URL,
            query_file=query,
            pilot_date=pilot_date,
            output_path=output,
            timeout_seconds=7.0,
            adapter_page_delay_seconds=0.0,
            inter_database_delay_seconds=2.0,
            adapter_directory=root,
        )
        return config, query, output

    @staticmethod
    def successful_result(database: str, total: int = 4, records: int = 1) -> dict:
        label = "Compendex" if database == "compendex" else "Inspec"
        return {
            "total": total,
            "results_retrieved": records,
            "results": [{"title": "must not be retained"}] if records else [],
            "output_metadata": {
                "status": "partial",
                "stopped_reason": "max_pages",
                "total_is_exact": True,
                "source": f"{label} (Engineering Village)",
                "databases": [database],
                "database_mask": ev.DATABASE_MASKS[database],
                "database_selection_mode": "individual_database",
                "selected_database_scope": label,
                "source_entries_retrieved_by_database": {database: records},
            },
        }

    def test_dry_run_writes_no_source_request_and_is_create_only(self):
        with tempfile.TemporaryDirectory() as directory:
            config, _, output = self.make_config(directory, execute=False)
            calls: list[str] = []

            def forbidden(*_args, **_kwargs):
                calls.append("called")
                raise AssertionError("dry run must not call an adapter")

            status, receipt = ev.run_paired_diagnostic(
                config,
                adapter_calls={"compendex": forbidden, "inspec": forbidden},
            )
            self.assertEqual(status, 0)
            self.assertEqual(receipt["result"]["classification"], "dry_run")
            self.assertEqual(calls, [])
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text())["mode"], "dry_run")
            collision_status, _ = ev.run_paired_diagnostic(
                config,
                adapter_calls={"compendex": forbidden, "inspec": forbidden},
            )
            self.assertEqual(collision_status, 1)

    def test_success_is_one_paired_operation_with_two_explicit_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            config, query, output = self.make_config(directory)
            calls: list[tuple[str, str, dict]] = []

            def compendex(value: str, **kwargs):
                calls.append(("compendex", value, kwargs))
                return self.successful_result("compendex")

            def inspec(value: str, **kwargs):
                calls.append(("inspec", value, kwargs))
                return self.successful_result("inspec")

            sleeps: list[float] = []
            status, receipt = ev.run_paired_diagnostic(
                config,
                adapter_calls={"compendex": compendex, "inspec": inspec},
                sleeper=sleeps.append,
            )
            self.assertEqual(status, 0)
            self.assertEqual(receipt["accounting"]["campaign_source_operation_count"], 1)
            self.assertEqual(receipt["accounting"]["campaign_source_operation_maximum"], 1)
            self.assertEqual(receipt["accounting"]["database_requests_planned"], 2)
            self.assertEqual(receipt["accounting"]["database_requests_performed"], 2)
            self.assertEqual(receipt["result"]["classification"], "paired_count_control_diagnostic_complete")
            self.assertEqual(receipt["totals"]["compendex"], 4)
            self.assertEqual(receipt["totals"]["inspec"], 4)
            self.assertIsNone(receipt["totals"]["paired"])
            self.assertEqual(sleeps, [2.0])
            self.assertEqual([entry[0] for entry in calls], ["compendex", "inspec"])
            self.assertEqual(calls[0][1], query.read_text(encoding="utf-8"))
            for _, _, kwargs in calls:
                self.assertEqual(kwargs["cdp_url"], ev.DEFAULT_CDP_URL)
                self.assertEqual(kwargs["limit"], 1)
                self.assertEqual(kwargs["max_pages"], 1)
                self.assertEqual(kwargs["year_start"], 2011)
                self.assertEqual(kwargs["year_end"], 2026)
                self.assertFalse(kwargs["require_complete"])
            self.assertEqual(receipt["result"]["records_retained"], 0)
            self.assertNotIn("must not be retained", json.dumps(receipt))
            serialized = output.read_text(encoding="utf-8")
            self.assertEqual(json.loads(serialized), receipt)

    def test_first_database_failure_stops_the_paired_event_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            config, _, output = self.make_config(directory)
            calls: list[str] = []

            def compendex(*_args, **_kwargs):
                calls.append("compendex")
                raise RuntimeError("private source failure must not be serialized")

            def inspec(*_args, **_kwargs):
                calls.append("inspec")
                return self.successful_result("inspec")

            status, receipt = ev.run_paired_diagnostic(
                config,
                adapter_calls={"compendex": compendex, "inspec": inspec},
            )
            self.assertEqual(status, 1)
            self.assertEqual(calls, ["compendex"])
            self.assertEqual(receipt["accounting"]["database_requests_performed"], 1)
            self.assertEqual(receipt["totals"], {
                "paired": None,
                "compendex": None,
                "inspec": None,
                "paired_total_basis": "not_inferred_from_separate_database_requests",
            })
            self.assertEqual(
                receipt["database_requests"][1]["classification"],
                "paired_event_stopped_after_first_request",
            )
            self.assertNotIn("private source failure", output.read_text(encoding="utf-8"))

    def test_explicit_native_zero_is_zero_but_nonexact_zero_is_null(self):
        with tempfile.TemporaryDirectory() as directory:
            config, _, output = self.make_config(directory)

            def zero(database: str, *, exact: bool):
                label = "Compendex" if database == "compendex" else "Inspec"
                return {
                    "total": 0,
                    "results_retrieved": 0,
                    "results": [],
                    "output_metadata": {
                        "status": "success",
                        "stopped_reason": "zero_results",
                        "total_is_exact": exact,
                        "source": f"{label} (Engineering Village)",
                        "databases": [database],
                        "database_mask": ev.DATABASE_MASKS[database],
                        "database_selection_mode": "individual_database",
                        "selected_database_scope": label,
                        "source_entries_retrieved_by_database": {database: 0},
                    },
                }

            status, receipt = ev.run_paired_diagnostic(
                config,
                adapter_calls={
                    "compendex": lambda query, **kwargs: zero("compendex", exact=True),
                    "inspec": lambda query, **kwargs: zero("inspec", exact=True),
                },
                sleeper=lambda _seconds: None,
            )
            self.assertEqual(status, 0)
            self.assertEqual(receipt["totals"]["compendex"], 0)
            self.assertEqual(receipt["totals"]["inspec"], 0)
            self.assertTrue(receipt["database_requests"][0]["explicit_native_zero"])

            output.unlink()
            status, receipt = ev.run_paired_diagnostic(
                config,
                adapter_calls={
                    "compendex": lambda query, **kwargs: zero("compendex", exact=False),
                    "inspec": lambda query, **kwargs: zero("inspec", exact=True),
                },
                sleeper=lambda _seconds: None,
            )
            self.assertEqual(status, 1)
            self.assertIsNone(receipt["totals"]["compendex"])
            self.assertEqual(receipt["totals"]["inspec"], None)

    def test_exact_shared_endpoint_and_terminal_lf_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            config, query, output = self.make_config(directory)
            bad_endpoint = config.__class__(
                **{**config.__dict__, "cdp_url": "http://127.0.0.1:9223"}
            )
            status, _ = ev.run_paired_diagnostic(
                bad_endpoint,
                adapter_calls={"compendex": lambda *_a, **_k: {}, "inspec": lambda *_a, **_k: {}},
            )
            self.assertEqual(status, 1)
            query.write_bytes(b"no terminal lf")
            invalid = config.__class__(**{**config.__dict__, "query_file": query, "output_path": output.with_name("other.json")})
            status, _ = ev.run_paired_diagnostic(
                invalid,
                adapter_calls={"compendex": lambda *_a, **_k: {}, "inspec": lambda *_a, **_k: {}},
            )
            self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
