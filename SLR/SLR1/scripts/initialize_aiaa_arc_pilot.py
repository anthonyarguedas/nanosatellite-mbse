#!/usr/bin/env python3
"""Materialize the source-free AIAA ARC P01 allocation scaffold.

This helper only reads the shared templates and local protocol/dictionary files.
It creates a new campaign/attempt directory and empty, mutable pre-run
artifacts; it never contacts ARC and never creates source evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TASK_ID = "S-D10"
SOURCE_ID = "aiaa-arc"
METHOD_TYPE = "direct"
SOURCE_PACKET_RELATIVE = Path("SLR/SLR1/searches/sources/s-d10-aiaa-arc")
CAMPAIGN_TEMPLATE_RELATIVE = Path(
    "SLR/SLR1/searches/templates/pilot-campaign.template.json"
)
MANIFEST_TEMPLATE_RELATIVE = Path(
    "SLR/SLR1/searches/templates/pilot-manifest.template.json"
)
PROTOCOL_RELATIVE = Path("SLR/SLR1/protocol.md")
DICTIONARY_RELATIVE = Path("SLR/SLR1/searches/search-concept-dictionary.json")

GATE_IDS = (
    "G-SOURCE-BOUNDARY",
    "G-QUERY-TRANSPORT",
    "G-FIELD-BOUNDARY",
    "G-CONTROLLED-VOCABULARY",
    "G-DATE-CONTROL",
    "G-LANGUAGE-CONTROL",
    "G-CONTENT-CONTROL",
    "G-RETRIEVAL",
    "G-PAGINATION-CONTROL",
    "G-PAGE-IDENTITY",
    "G-COMPLETENESS",
    "G-FAILURE-BEHAVIOR",
)

# Only dependencies that are explicit in the P01 disposition are materialized;
# all other gates remain independent until runtime evidence establishes a link.
GATE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "G-FIELD-BOUNDARY": ("G-QUERY-TRANSPORT",),
    "G-PAGE-IDENTITY": ("G-PAGINATION-CONTROL",),
}

GATE_REQUIREMENTS: dict[str, str] = {
    "G-SOURCE-BOUNDARY": "P01 must establish the reviewed ARC source boundary.",
    "G-QUERY-TRANSPORT": "P01 must preserve the exact B1 query and AllField transport.",
    "G-FIELD-BOUNDARY": "P01 must establish the ARC AllField boundary.",
    "G-CONTROLLED-VOCABULARY": "P01 must not claim an unobserved controlled vocabulary.",
    "G-DATE-CONTROL": "P01 must retain the declared diagnostic date controls.",
    "G-LANGUAGE-CONTROL": "P01 must preserve the declared absence of a language filter.",
    "G-CONTENT-CONTROL": "P01 must retain the declared all-content control.",
    "G-RETRIEVAL": "P01 may establish only the bounded retrieval diagnostic.",
    "G-PAGINATION-CONTROL": "P01 must reconcile the rendered first-page range and size.",
    "G-PAGE-IDENTITY": "P01 must reconcile rendered DOI identity and any RIS identity.",
    "G-COMPLETENESS": "P01 must not claim strict completeness.",
    "G-FAILURE-BEHAVIOR": "P01 must preserve null, zero, cleanup, and output failure rules.",
}

NOW_PATTERN = re.compile(r"^(\d{8}T\d{6})([+-]\d{4})$")
HEX40_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class MaterializationError(ValueError):
    """Raised when the offline runtime allocation is unsafe or inconsistent."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise MaterializationError(f"could not read JSON template: {path}") from error
    if not isinstance(value, dict):
        raise MaterializationError(f"JSON template must contain an object: {path}")
    return value


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise MaterializationError(f"could not fingerprint local file: {path}") from error


def _parse_runtime_timestamp(value: str) -> tuple[str, str]:
    match = NOW_PATTERN.fullmatch(value)
    if match is None:
        raise MaterializationError(
            "--now must be UTC date output in YYYYMMDDTHHMMSS+0000 form"
        )
    try:
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%S%z")
    except ValueError as error:
        raise MaterializationError("--now is not a valid timestamp") from error
    if parsed.utcoffset() != timedelta(0):
        raise MaterializationError("--now must use the UTC +0000 offset")
    iso = parsed.astimezone(timezone.utc).isoformat(timespec="seconds")
    return value, iso


def _require_absent(path: Path, label: str) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing {label}: {path}")


def _write_new(path: Path, contents: bytes, label: str) -> None:
    _require_absent(path, label)
    try:
        with path.open("xb") as handle:
            handle.write(contents)
    except FileExistsError:
        raise
    except OSError as error:
        raise MaterializationError(f"could not create {label}: {path}") from error


def _initial_gate(gate_id: str, attempt_id: str) -> dict[str, Any]:
    suffix = gate_id.removeprefix("G-")
    return {
        "gate_id": gate_id,
        "checkpoint_id": f"CP-{suffix}-P01",
        "attempt_id": attempt_id,
        "requirement": GATE_REQUIREMENTS[gate_id],
        "depends_on": list(GATE_DEPENDENCIES.get(gate_id, ())),
        "status": "untested",
        "observed_basis": "untested",
        "original_observed_basis": "untested",
        "evidence": [],
        "reusable": False,
        "carried_forward": False,
        "carry_forward": None,
        "source_operation_count": 0,
        "semantic_impact": {
            "classification": "none",
            "review_effect": False,
            "rationale": "Runtime allocation has produced no source or semantic evidence.",
        },
        "invalidation": None,
        "notes": "Untested allocation state; no source result or evidence exists yet.",
    }


def _initial_terminal(timestamp: str) -> dict[str, Any]:
    return {
        "outcome": "blocked",
        "category": "technical",
        "ended_at": timestamp,
        "provider_failure": False,
        "source_writing_stopped": True,
        "browser_backed": False,
        "terminal_verification": "not_applicable",
        "cleanup_receipt": None,
        "lease_receipt": None,
        "cancelled_by": None,
        "reason": (
            "Pre-run allocation scaffold only; replace this placeholder with the "
            "attached P01 terminal outcome before checkpointing."
        ),
    }


def _build_materialization(
    root: Path, *, now: str, protocol_commit: str
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    now_id, timestamp = _parse_runtime_timestamp(now)
    if not HEX40_PATTERN.fullmatch(protocol_commit):
        raise MaterializationError("--protocol-commit must be a lowercase 40-character Git SHA")

    campaign_id = f"{TASK_ID}-C01-{now_id}"
    attempt_id = f"{TASK_ID}-P01-{now_id}"
    campaign_template = _load_json(root / CAMPAIGN_TEMPLATE_RELATIVE)
    manifest_template = _load_json(root / MANIFEST_TEMPLATE_RELATIVE)
    if tuple(campaign_template.get("capability_catalog", ())) != GATE_IDS:
        raise MaterializationError(
            "shared campaign template catalog is not the frozen S-D10 direct catalog"
        )

    protocol_path = root / PROTOCOL_RELATIVE
    dictionary_path = root / DICTIONARY_RELATIVE
    protocol_fingerprint = _sha256_file(protocol_path)
    dictionary_fingerprint = _sha256_file(dictionary_path)

    manifest = copy.deepcopy(manifest_template)
    manifest.update(
        {
            "pilot_id": attempt_id,
            "task_id": TASK_ID,
            "source_id": SOURCE_ID,
            "method_type": METHOD_TYPE,
            # The mutable pre-run manifest has no source execution or terminal
            # link yet. The campaign's allocation scaffold is updated after P01.
            "status": "partial",
            "started_at": timestamp,
            "ended_at": timestamp,
            "protocol_commit": protocol_commit,
            "operator": {
                "type": "llm_subagent",
                "model": None,
                "human_supervisor": None,
            },
            "interface": {
                "name": "AIAA Aerospace Research Central (ARC)",
                "url": "https://arc.aiaa.org/search/advanced",
                "access_route": "public_or_authorized_browser",
                "authenticated": False,
            },
            "executions": [],
            "checks": [],
            "artifacts": [],
            "campaign": {
                "campaign_id": campaign_id,
                "attempt_id": attempt_id,
            },
            "disposition": {
                "recommendation": "revise",
                "reason": "P01 allocation scaffold is materialized; terminal outcome is pending.",
                "semantic_change": False,
                "human_verification_required": [],
            },
        }
    )
    # Do not let a future template add a pre-run terminal claim to the mutable
    # manifest. The campaign projection is the only required allocation shape.
    manifest.pop("attempt_terminal", None)

    manifest_path = f"pilots/{attempt_id}/manifest.json"
    manifest_bytes = _json_bytes(manifest)
    terminal = _initial_terminal(timestamp)
    attempt = {
        "attempt_id": attempt_id,
        "sequence": 1,
        "manifest_path": manifest_path,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "immutable": True,
        "allocation": {
            "attempt_kind": "initial",
            "authorized_by": "controller",
            "authorization_decision_id": None,
            "prospectively_authorized": False,
            "allocated_at": timestamp,
        },
        "source_operations": {
            "predeclared_maximum": 2,
            "performed": 0,
            "operations": [],
        },
        "evidence": [],
        "terminal": terminal,
    }

    campaign = copy.deepcopy(campaign_template)
    campaign.update(
        {
            "campaign_id": campaign_id,
            "task_id": TASK_ID,
            "source_id": SOURCE_ID,
            "method_type": METHOD_TYPE,
            "protocol_fingerprint": protocol_fingerprint,
            "dictionary_fingerprint": dictionary_fingerprint,
            "capability_catalog": list(GATE_IDS),
            "status": "in_progress",
            "created_at": timestamp,
            "updated_at": timestamp,
            "diagnostic_only": True,
            "screening_performed": False,
            "candidate_import_permitted": False,
            "candidate_records_imported": 0,
            "retry_policy": {
                "policy_id": "RP-AIAA-P01",
                "maximum_retries": 0,
                "passive_wait_delays_seconds": [],
                "attempted": 0,
                "completed": 0,
                "preauthorized_same_tab_busy_reissue": False,
            },
            "controller_authorization": {
                "technical_corrective_attempts_authorized": True,
                "maximum_additional_attempts": 2,
                "maximum_technical_corrective_attempts": 2,
                "maximum_methodological_revision_attempts": 1,
                "maximum_source_operations_per_attempt": 2,
                "rationale": (
                    "Controller may allocate bounded behavior-preserving AIAA "
                    "technical corrections without changing review semantics."
                ),
            },
            "attempts": [attempt],
            "gate_status_snapshots": [],
            "capability_gates": [
                _initial_gate(gate_id, attempt_id) for gate_id in GATE_IDS
            ],
            "decisions": [],
            "cancellation": None,
            "acceptance": None,
        }
    )
    return campaign, manifest, manifest_path, attempt_id


def materialize(
    root: Path, *, now: str, protocol_commit: str
) -> tuple[Path, Path]:
    """Create the new AIAA campaign and mutable P01 manifest, without evidence."""
    root = root.expanduser().resolve()
    campaign, manifest, manifest_path, attempt_id = _build_materialization(
        root, now=now, protocol_commit=protocol_commit
    )
    source_packet = root / SOURCE_PACKET_RELATIVE
    if not source_packet.is_dir() or source_packet.is_symlink():
        raise MaterializationError(f"AIAA source packet is not a regular directory: {source_packet}")
    campaign_path = source_packet / "campaign.json"
    attempt_dir = source_packet / "pilots" / attempt_id
    manifest_destination = source_packet / manifest_path
    _require_absent(campaign_path, "AIAA campaign")
    _require_absent(attempt_dir, "AIAA attempt directory")
    _require_absent(manifest_destination, "AIAA pilot manifest")

    try:
        attempt_dir.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        raise MaterializationError(f"could not create AIAA attempt directory: {attempt_dir}") from error
    _write_new(manifest_destination, _json_bytes(manifest), "AIAA pilot manifest")
    _write_new(campaign_path, _json_bytes(campaign), "AIAA campaign")
    return campaign_path, manifest_destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the offline AIAA ARC P01 campaign/manifest allocation "
            "from the shared templates; no source work is performed."
        )
    )
    parser.add_argument("--root", type=Path, required=True, help="Nanosatellite repository root")
    parser.add_argument(
        "--now",
        required=True,
        help="One UTC ID timestamp in YYYYMMDDTHHMMSS+0000 form",
    )
    parser.add_argument(
        "--protocol-commit",
        required=True,
        help="Current local 40-character Git commit for the manifest",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        campaign_path, manifest_path = materialize(
            args.root, now=args.now, protocol_commit=args.protocol_commit
        )
    except (FileExistsError, MaterializationError) as error:
        print(f"initialize_aiaa_arc_pilot: {error}")
        return 1
    print(f"campaign={campaign_path}")
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
