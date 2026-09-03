#!/usr/bin/env python3
"""Build the predeclared OATD Pilot 004 shared-population plan."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

from queries import (
    BLOCK_TERMS,
    LOCAL_SCHEDULE,
    P_QUERY,
    PROTOCOL_COMMIT,
    SCHEDULE_IDS,
    TERM_COUNTS,
    TERM_SNAPSHOT_PATH,
    file_sha256,
)

PILOT = "004"
SCHEMA = "oatd-pilot-004-event-plan/v1"
ADAPTER_PLAN_SCHEMA = "oatd-local-matching-plan/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[1]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific" / "oatd" / "pilots" / PILOT
DEFAULT_EVENT_PLAN = PILOT_ROOT / "searches" / "event-plan.json"
DEFAULT_LOCAL_PLAN = PILOT_ROOT / "searches" / "local-matching-plan.json"
ADAPTER_ROOT = Path.home() / "agent-tools"
ADAPTER_PATH = ADAPTER_ROOT / "internet/skills/browser/scripts/search_oatd.py"
ADAPTER_FILES = {
    "entrypoint": ADAPTER_PATH,
    "browser_helpers": ADAPTER_PATH.with_name("_browser_search_utils.py"),
    "output_loader": ADAPTER_PATH.with_name("_output_utils.py"),
    "output_implementation": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_output_utils.py"
    ),
    "merge_contract": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_merge_contract.py"
    ),
}
SOURCE_AFFECTING_SCRIPTS = (
    SCRIPT_DIR / "queries.py",
    SCRIPT_DIR / "build_plan.py",
    SCRIPT_DIR / "run_pilot.py",
)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def relative_to_repository(path: Path) -> str:
    return str(path.resolve().relative_to(REPOSITORY_ROOT.resolve()))


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot004_adapter_for_plan", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load the OATD adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def local_plan_payload(adapter: Any) -> dict[str, Any]:
    plan = adapter.build_local_matching_plan(LOCAL_SCHEDULE)
    return {
        "schema_version": plan.schema_version,
        "matcher_version": plan.matcher_version,
        "expressions": [
            {
                "id": expression.expression_id,
                "expression": expression.expression,
                "sha256": expression.sha256,
            }
            for expression in plan.expressions
        ],
        "plan_sha256": plan.plan_sha256,
    }


def screenshot_names(output: str) -> dict[str, str]:
    path = Path(output)
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.name
    return {
        "search_page": str(path.with_name(f"{stem}.search-page.png")),
        "results_page": str(path.with_name(f"{stem}.results-page.png")),
    }


def build(
    event_plan_path: Path, local_plan_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    adapter = load_adapter()
    if adapter.ADAPTER_VERSION != "10":
        raise RuntimeError("OATD Pilot 004 requires adapter v10")
    local_plan = local_plan_payload(adapter)
    if local_plan["schema_version"] != ADAPTER_PLAN_SCHEMA:
        raise RuntimeError("The OATD adapter returned an unexpected local-plan schema")

    output = "P-shared.json"
    checkpoint = "checkpoint/P-shared.checkpoint.json"
    local_plan_relative = str(
        local_plan_path.resolve().relative_to(PILOT_ROOT.resolve())
    )
    output_relative = f"searches/{output}"
    event = {
        "event_id": "P-shared",
        "source_submission": "P",
        "purpose": (
            "Submit only the complete literal population block, retain every stable "
            "OATD record, then apply all nine current schedule expressions locally as "
            "annotations."
        ),
        "query": P_QUERY,
        "query_characters": len(P_QUERY),
        "query_sha256": digest_text(P_QUERY),
        "language": "English",
        "language_source_value": "(en OR eng OR english)",
        "year_start": 2011,
        "year_end": 2026,
        "diagnostic_exact_cutoff": "2026-08-29",
        "page_size": 100,
        "limit": 2000,
        "max_pages": 30,
        "timeout_seconds": 180,
        "page_delay_seconds": 0.75,
        "detail_delay_seconds": 0.5,
        "busy_retries": 2,
        "busy_retry_delay_seconds": 60,
        "shared_population_harvest": True,
        "local_matching_plan": local_plan_relative,
        "local_matching_plan_sha256": file_sha256(local_plan_path),
        "checkpoint": f"searches/{checkpoint}",
        "output": output_relative,
        "screenshots": screenshot_names(output_relative),
        "do_not_merge": True,
    }
    plan = {
        "schema_version": SCHEMA,
        "source": "Open Access Theses and Dissertations (OATD)",
        "source_id": "oatd",
        "platform": "OATD",
        "pilot": PILOT,
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Pilot the current no-proximity schedule through one lossless P-only "
            "source harvest followed by annotation-only local matching."
        ),
        "route_rationale": (
            "Every schedule partition contains P. The complete controlled P stable-ID "
            "set is therefore a no-loss candidate superset. OATD route and rate limits "
            "make nine large native schedule submissions unsafe."
        ),
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
            "files": {
                name: {
                    "path": f"~/agent-tools/{path.relative_to(ADAPTER_ROOT)}",
                    "sha256": file_sha256(path),
                }
                for name, path in ADAPTER_FILES.items()
            },
            "mandatory_automatic_screenshots": True,
            "screenshot_opt_out": False,
        },
        "source_affecting_scripts": {
            relative_to_repository(path): file_sha256(path)
            for path in SOURCE_AFFECTING_SCRIPTS
        },
        "term_snapshot": {
            "path": relative_to_repository(TERM_SNAPSHOT_PATH),
            "sha256": file_sha256(TERM_SNAPSHOT_PATH),
            "term_counts": TERM_COUNTS,
            "blocks": {key: list(values) for key, values in BLOCK_TERMS.items()},
        },
        "translation": {
            "source_submission_count": 1,
            "source_submission": "P only",
            "source_literal": "one straight-double-quoted literal",
            "local_literal": "one straight-double-quoted lexical phrase",
            "boolean": "uppercase AND and OR with explicit parentheses",
            "wildcards": False,
            "proximity": False,
            "pair_expansion": False,
            "controlled_vocabulary": False,
            "local_schedule_ids": list(SCHEDULE_IDS),
            "local_expression_lengths": {
                key: len(value) for key, value in LOCAL_SCHEDULE.items()
            },
            "local_expression_sha256": {
                key: digest_text(value) for key, value in LOCAL_SCHEDULE.items()
            },
        },
        "controls": {
            "source": "full OATD index",
            "language": "English metadata",
            "year_window": "2011-2026 inclusive calendar bounds",
            "exact_cutoff_handling": "screen 2026 records against 2026-08-29",
            "country": None,
            "degree": None,
            "level": None,
            "creative_commons": False,
            "document_type": None,
            "sort": "source-rendered Relevance",
            "page_size": 100,
            "screenshots": (
                "mandatory configured search-page and verified first-results PNGs "
                "beside the JSON"
            ),
        },
        "local_matching_plan": {
            "path": local_plan_relative,
            "sha256": file_sha256(local_plan_path),
            "schema_version": local_plan["schema_version"],
            "matcher_version": local_plan["matcher_version"],
            "plan_sha256": local_plan["plan_sha256"],
            "expression_count": len(local_plan["expressions"]),
        },
        "acceptance_checks": [
            "The source receives exactly one P-only query.",
            "The source reads back the exact effective P, English, and year query.",
            "Two complete source card-ID snapshots have equal stable-ID sets.",
            "Every unique source ID has one complete normalized detail record.",
            "Every retained record has all nine local annotation outcomes.",
            "Local negatives remove no source record.",
            "Both mandatory sibling screenshot PNGs match their JSON receipts.",
            "No wildcard, proximity operator, pair expansion, or result refinement is used.",
        ],
        "event_count": 1,
        "events": [event],
    }
    return local_plan, plan


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-plan", type=Path, default=DEFAULT_EVENT_PLAN)
    parser.add_argument("--local-plan", type=Path, default=DEFAULT_LOCAL_PLAN)
    args = parser.parse_args()
    if args.event_plan.resolve() == args.local_plan.resolve():
        raise RuntimeError("Event and local plans need distinct paths")
    # Write the local plan first because the event plan binds its exact bytes.
    adapter = load_adapter()
    local_plan = local_plan_payload(adapter)
    write_new(args.local_plan, local_plan)
    _local, event_plan = build(args.event_plan, args.local_plan)
    if _local != local_plan:
        raise RuntimeError("The local plan changed while the event plan was built")
    write_new(args.event_plan, event_plan)
    print(
        json.dumps(
            {
                "event_plan": str(args.event_plan),
                "local_plan": str(args.local_plan),
                "event_count": 1,
                "local_expression_count": len(local_plan["expressions"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
