#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Validate the bounded Springer Link to Nature canonical mapping."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_DIR / "source-specific" / "springer-nature-link" / "pilots" / "005"
DEFAULT_PLAN = PILOT_ROOT / "searches" / "event-plan.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "adapter-validation.json"
DEFAULT_ADAPTER = (
    Path.home()
    / "agent-tools"
    / "internet"
    / "skills"
    / "browser"
    / "scripts"
    / "search_springer_link.py"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def write_json_create_only(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_adapter(path: Path, minimum_version: int) -> Any:
    spec = importlib.util.spec_from_file_location("springer_p005_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Springer adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if int(module.ADAPTER_VERSION) < minimum_version:
        raise RuntimeError(f"Springer adapter version {minimum_version}+ is required")
    return module


async def validate_live(args: argparse.Namespace) -> dict[str, Any]:
    plan = load_json(args.plan)
    if (
        plan.get("schema_version") != "springer-nature-link-pilot005-event-plan/v1"
        or plan.get("navigate_to_nature") is not False
        or plan.get("check_final_response_status") is not False
    ):
        raise RuntimeError("Springer Pilot 005 plan is invalid")
    adapter = load_adapter(args.adapter, plan["adapter_minimum_version"])
    from playwright.async_api import async_playwright

    started_at = now()
    lease = None
    detail = None
    navigation = None
    owned_page_closed = False
    async with async_playwright() as playwright:
        try:
            lease = await adapter.open_springer_owned_page(
                playwright,
                cdp_url=args.cdp_url,
                headless=False,
                timeout_seconds=60.0,
                chrome_executable=None,
            )
            navigation = await adapter.navigate_to_springer_detail(
                lease.page,
                plan["source_card_path"],
                60.0,
                allow_changed_detail_route=False,
            )
            detail = await adapter.wait_for_springer_detail(
                lease.page,
                navigation=navigation,
                source_card_title=plan["source_card_title"],
                timeout_seconds=60.0,
                allow_changed_detail_route=False,
            )
        finally:
            page = lease.page if lease is not None else None
            await adapter.close_springer_owned_page(lease)
            owned_page_closed = bool(page is not None and page.is_closed())
    if detail is None or navigation is None:
        raise RuntimeError("Springer mapping validation produced no detail evidence")
    errors = []
    if navigation.final_url != plan["expected_link_url"]:
        errors.append("Final Link URL changed")
    if navigation.redirect_count != plan["expected_redirect_count"]:
        errors.append("Redirect count changed")
    if detail.source_card_path != plan["source_card_path"]:
        errors.append("Source card identity changed")
    if detail.resolved_detail_path != plan["source_card_path"]:
        errors.append("Resolved Link route changed")
    if detail.canonical_link != plan["expected_canonical_link"]:
        errors.append("Nature canonical mapping changed")
    if detail.title != plan["source_card_title"]:
        errors.append("Visible title changed")
    if plan["require_visible_abstract"] and not detail.abstract:
        errors.append("Visible Link abstract was absent")
    if detail.route_alias is not None:
        errors.append("Exact Link route acquired a navigation alias")
    if not owned_page_closed:
        errors.append("Adapter-owned page cleanup failed")
    return {
        "schema_version": "springer-nature-link-pilot005-adapter-validation/v1",
        "pilot": "005",
        "source": "Springer Nature Link",
        "status": "pass" if not errors else "fail",
        "diagnostic_only": True,
        "do_not_merge": True,
        "merge_eligible": False,
        "plan": str(args.plan.relative_to(PILOT_ROOT)),
        "plan_sha256": file_sha256(args.plan),
        "adapter": {
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": file_sha256(args.adapter),
        },
        "observed": {
            "source_card_path": detail.source_card_path,
            "source_card_url": navigation.source_url,
            "final_url": navigation.final_url,
            "redirect_count": navigation.redirect_count,
            "route_alias": detail.route_alias,
            "canonical_link": detail.canonical_link,
            "title": detail.title,
            "abstract_available": bool(detail.abstract),
            "abstract_characters": len(detail.abstract),
            "publication_date": detail.publication_date or None,
            "publication_date_precision": detail.publication_date_precision,
            "final_response_status_checked": False,
            "nature_url_navigated": False,
            "owned_page_closed": owned_page_closed,
        },
        "started_at": started_at,
        "completed_at": now(),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222")
    args = parser.parse_args()
    result = asyncio.run(validate_live(args))
    write_json_create_only(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
