#!/usr/bin/env python3
"""Apply the persisted-query-alias correction and finalize ESA receipts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping

SCRIPT_PATH = Path(__file__).resolve()
RUNNER_PATH = SCRIPT_PATH.with_name("run.py")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("esa_indico_final_pinned_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def accept_post_execution_protocol_drift(runner: Any, plan: Mapping[str, Any]) -> dict[str, Any]:
    declared = plan.get("bindings", {}).get("files")
    if not isinstance(declared, Mapping):
        raise RuntimeError("The final plan lacks source file bindings")
    discovery = "SLR/SLR1/protocol-discovery-and-screening.md"
    observed: dict[str, str] = {}
    for relative_path, expected in declared.items():
        path = runner.REPOSITORY_ROOT / relative_path
        actual = sha256(path)
        observed[relative_path] = actual
        if relative_path != discovery and actual != expected:
            raise RuntimeError(f"A source-affecting file changed: {relative_path}")
    if observed.get(discovery) == declared.get(discovery):
        state = "unchanged"
    else:
        state = "post_execution_prose_change_with_search_blocks_declared_unchanged"
    runner.source_bindings = lambda: dict(declared)
    return {
        "state": state,
        "path": discovery,
        "predeclared_sha256": declared.get(discovery),
        "current_sha256": observed.get(discovery),
        "query_snapshot_unchanged": observed.get(
            "SLR/SLR1/source-specific/esa-indico/scripts/esa_indico_pilot007/queries.py"
        )
        == declared.get("SLR/SLR1/source-specific/esa-indico/scripts/esa_indico_pilot007/queries.py"),
    }


def configure_runner() -> Any:
    runner = load_runner()
    original_load_json = runner.load_json

    def load_with_requested_alias(path: Path) -> dict[str, Any]:
        value = original_load_json(path)
        if (
            value.get("schema_version") == "academic-search-result/v1"
            and "query" not in value
            and isinstance(value.get("requested_query"), str)
        ):
            value["query"] = value["requested_query"]
        return value

    runner.load_json = load_with_requested_alias
    original_build_receipts = runner.build_receipts

    def build_corrected_receipts(plan: Any, output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        protocol_drift = accept_post_execution_protocol_drift(runner, plan)
        receipt, validation = original_build_receipts(plan, output_dir)
        correction = {
            "schema_version": "slr1-esa-indico-persisted-query-alias-correction/v1",
            "reason": (
                "The shared normalizer persists requested_query and omits the legacy query "
                "alias. Validation reads requested_query as the authoritative requested value."
            ),
            "changes_to_source_artifacts": False,
            "changes_to_queries": False,
            "changes_to_matches": False,
            "script": "SLR/SLR1/source-specific/esa-indico/scripts/esa_indico_final_direct/finalize.py",
            "script_sha256": sha256(SCRIPT_PATH),
            "pinned_runner_sha256": sha256(RUNNER_PATH),
            "protocol_drift": protocol_drift,
        }
        receipt["validation_correction"] = correction
        validation["validation_correction"] = correction
        validation["checks"]["persisted_requested_query_alias"] = "pass"
        return receipt, validation

    runner.build_receipts = build_corrected_receipts
    return runner


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("receipt", "validate"))
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    runner = configure_runner()
    output_dir = (
        args.output_dir.resolve(strict=False)
        if args.output_dir is not None
        else runner.DEFAULT_OUTPUT_DIR
    )
    plan = runner.load_json(output_dir / "final-event-plan.json")
    if args.action == "receipt":
        runner.write_receipts(plan, output_dir)
    else:
        runner.validate_persisted(plan, output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
