#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Focused, source-free Wiley adapter checks for S-D05-P01."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ADAPTER = Path.home() / "agent-tools/academic-research/skills/academic-search/scripts/search_wiley_online_library.py"
BROWSER_HELPER = ADAPTER.with_name("_browser_search_utils.py")
OUTPUT_HELPER = ADAPTER.with_name("_output_utils.py")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_adapter():
    spec = importlib.util.spec_from_file_location("s_d05_wiley_adapter_probe", ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Wiley adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expected_error(callable_):
    try:
        callable_()
    except Exception as error:  # expected pure-input rejection
        return {"raised": type(error).__name__, "message": str(error)}
    raise AssertionError("expected input rejection did not occur")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.exists() or output.is_symlink():
        raise SystemExit(f"refusing to overwrite receipt: {output}")

    adapter = load_adapter()
    source = ADAPTER.read_text(encoding="utf-8")
    checks: dict[str, object] = {}

    # These calls are pure local validation; they do not create a browser page
    # or make a source/network request.
    checks["query_maximum"] = expected_error(
        lambda: adapter.validate_query("x" * (adapter.MAX_QUERY_CHARACTERS + 1))
    )
    checks["strict_contract"] = expected_error(
        lambda: adapter.validate_complete_contract(
            required=True,
            content="collections",
            count_only=True,
            passes=1,
            sort="Relevance",
            date_bounds=None,
            native_export_dir=None,
        )
    )
    checks["fresh_browser_conflict"] = expected_error(
        lambda: adapter.validate_cli_args(
            adapter.build_parser().parse_args(
                [
                    "--query", "offline-sentinel",
                    "--output-path", "offline.json",
                    "--fresh-browser",
                    "--cdp-url", "http://127.0.0.1:9236",
                ]
            )
        )
    )

    bounds = adapter.resolve_date_bounds(
        year_start=None,
        year_end=None,
        date_start=adapter.date(2011, 1, 1),
        date_end=adapter.date(2026, 8, 24),
    )
    checks["exact_date_projection"] = {
        "exact_start": bounds.exact_start.isoformat(),
        "exact_end": bounds.exact_end.isoformat(),
        "source_start": bounds.source_start.isoformat(),
        "source_end": bounds.source_end.isoformat(),
        "client_filter_required": bounds.client_filter_required,
    }

    with tempfile.TemporaryDirectory(prefix="s-d05-wiley-no-clobber-") as directory:
        temporary = Path(directory)
        json_path = temporary / "preexisting.json"
        csv_path = temporary / "preexisting.csv"
        json_before = b'{"sentinel":"preexisting"}\n'
        csv_before = b"sentinel,preexisting\n"
        json_path.write_bytes(json_before)
        csv_path.write_bytes(csv_before)

        adapter.atomic_write_json(json_path, {"sentinel": "replaced"})
        adapter.atomic_write_csv(
            csv_path,
            [],
            query="offline-sentinel",
            source_total=0,
        )
        json_after = json_path.read_bytes()
        csv_after = csv_path.read_bytes()
        checks["json_no_clobber"] = {
            "preexisting_file_was_replaced": json_after != json_before,
            "before_sha256": hashlib.sha256(json_before).hexdigest(),
            "after_sha256": hashlib.sha256(json_after).hexdigest(),
            "after_contains_replacement_sentinel": b"replaced" in json_after,
        }
        checks["csv_no_clobber"] = {
            "preexisting_file_was_replaced": csv_after != csv_before,
            "before_sha256": hashlib.sha256(csv_before).hexdigest(),
            "after_sha256": hashlib.sha256(csv_after).hexdigest(),
            "after_starts_with_expected_header": csv_after.startswith(b"Search source,"),
        }

    json_replaced = checks["json_no_clobber"]["preexisting_file_was_replaced"]
    csv_replaced = checks["csv_no_clobber"]["preexisting_file_was_replaced"]
    if not json_replaced or not csv_replaced:
        raise AssertionError("the expected no-clobber defect was not reproduced")

    receipt = {
        "schema_version": "slr1-s-d05-offline-adapter-check/v1",
        "source_requests_made": 0,
        "browser_pages_created": 0,
        "adapter": {
            "path": str(ADAPTER),
            "sha256": sha256(ADAPTER),
            "browser_helper_sha256": sha256(BROWSER_HELPER),
            "output_helper_sha256": sha256(OUTPUT_HELPER),
        },
        "static_call_sites": {
            "normal_json_save_call_present": "atomic_write_json(output_path, result)" in source,
            "normal_csv_save_call_present": "atomic_write_normalized_csv(csv_path, result)" in source,
            "native_ris_has_explicit_existing_path_guard": "native_path.exists() or native_path.is_symlink()" in source,
            "normal_output_path_existing_file_guard_present": "output_path.exists()" in source,
        },
        "checks": checks,
        "code_issue": {
            "value": True,
            "classification": "demonstrated_no_clobber_failure",
            "scope": "The normal JSON and optional normalized CSV save paths replace pre-existing local files through os.replace without an existing-output refusal. Native RIS has a separate guard, but it does not protect the normal result artifacts.",
            "required_action": "Separate adapter code-fix: add atomic no-clobber publication for normal JSON and CSV outputs (including error artifacts), then add focused regression tests; do not rerun source work under this pilot ID.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
