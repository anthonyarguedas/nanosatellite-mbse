#!/usr/bin/env python3
"""Retry the predeclared PSR2 strict predicate diagnostic after a context failure."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
TARGET_HELPER = REPOSITORY_ROOT / "SLR/SLR1/scripts/scopus_pilot015/run_pilot.py"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def load_target_helper():
    spec = importlib.util.spec_from_file_location("scopus_pilot016_target_helper", TARGET_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {TARGET_HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists() or args.receipt.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.receipt}")
    plan = load(args.plan)
    adapter = Path(plan["adapter"]["path"])
    wrapper = REPOSITORY_ROOT / plan["wrapper"]["path"]
    if digest(adapter) != plan["adapter"]["sha256"] or digest(wrapper) != plan["wrapper"]["sha256"]:
        raise SystemExit("Predeclared adapter or wrapper changed")
    output = args.pilot_root / "searches" / plan["output"]
    stderr_path = args.pilot_root / "searches" / "debug-stderr.txt"
    for path in (
        output,
        output.with_name(f"{output.stem}.search-page.png"),
        output.with_name(f"{output.stem}.results-page.png"),
        stderr_path,
    ):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"Refusing to overwrite {path}")
    helper = load_target_helper()
    cdp_url = "http://127.0.0.1:9222"
    target_id = helper.create_ephemeral_scopus_target(cdp_url)
    command = [
        "uv", "run", "--with", "playwright>=1.48", str(wrapper),
        "--query", plan["query"],
        "--year-end", "2026",
        "--result-scope", "documents",
        "--page-size", str(plan["page_size"]),
        "--limit", str(plan["limit"]),
        "--max-pages", str(plan["max_pages"]),
        "--timeout", "180",
        "--page-delay-seconds", "0.75",
        "--skip-full-abstracts",
        "--require-complete",
        "--cdp-url", cdp_url,
        "--target-id", target_id,
        "--output-path", str(output),
        "--prisma-run-id", "pilot-scopus-017-PSR2-debug-retry",
        "--prisma-review-id", "slr1-pilot-017",
        "--prisma-strategy-reference", "slr1-scopus-psr2-strict-predicate-debug-v1",
        "--prisma-strategy-version", "3194156e90497186664260a8e86435e78d2e2aa1",
        "--prisma-phase", "pilot",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", "PSR2-debug",
        "--prisma-partition-label", "PSR2-debug",
        "--prisma-partition-description", "Scopus Pilot 017 ID-free PSR2 strict predicate diagnostic retry",
    ]
    started = now()
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        target_closed = helper.close_ephemeral_target(cdp_url, target_id)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.write_text(result.stderr, encoding="utf-8")
    diagnostic_lines = [
        line.split("=", 1)[1]
        for line in result.stderr.splitlines()
        if line.startswith("SCOPUS_STRICT_PREDICATE_DIAGNOSTIC=")
    ]
    diagnostics = [json.loads(line) for line in diagnostic_lines]
    receipt = {
        "schema_version": "scopus-psr2-strict-predicate-diagnostic-retry-run/v1",
        "pilot": "017",
        "diagnostic_only": True,
        "do_not_merge": True,
        "target_identifier_retained": False,
        "fresh_authorized_target_created": True,
        "ephemeral_target_close_requested": target_closed,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "started_at_utc": started,
        "completed_at_utc": now(),
        "exit_code": result.returncode,
        "artifact": str(output.relative_to(args.pilot_root)),
        "artifact_written": output.is_file(),
        "debug_stderr": str(stderr_path.relative_to(args.pilot_root)),
        "debug_stderr_sha256": digest(stderr_path),
        "strict_predicate_diagnostics": diagnostics,
        "diagnostic_observed": bool(diagnostics),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exit_code": result.returncode, "diagnostics": diagnostics}))
    return 0 if diagnostics else 1


if __name__ == "__main__":
    raise SystemExit(main())
