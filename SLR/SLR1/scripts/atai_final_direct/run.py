#!/usr/bin/env python3
"""Plan, execute, and assess final ATAI direct discovery searches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)
SOURCE_UNION_TOOL = (
    Path.home() / "agent-tools/internet/skills/browser/scripts/source_union_receipt.py"
)
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/atai_pilot008/queries.py"
TERM_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/atai_pilot007/queries.py"
PILOT_ASSESSMENT = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/advanced-technologies-aerospace-index"
    / "pilots/008/searches/assessment.json"
)
SOURCE_GUIDELINE = (
    REPOSITORY_ROOT
    / "SLR/SLR1/source-specific/advanced-technologies-aerospace-index"
    / "source-specific-guidelines.md"
)
MAIN_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"

PLAN_SCHEMA = "slr1-atai-final-direct-plan/v1"
RUN_SCHEMA = "slr1-atai-final-direct-run/v1"
ASSESSMENT_SCHEMA = "slr1-atai-final-direct-assessment/v1"
MARKER_SCHEMA = "slr1-atai-final-output-commit-marker/v1"

SOURCE = "Advanced Technologies & Aerospace Index"
SOURCE_ID = "proquest_aerospace_index"
REVIEW_NAMESPACE = "main"
REVIEW_ID = "slr1-1.1-restart"
PHASE = "identification"
STRATEGY_REFERENCE = "slr1-atai-main-direct-v1"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-24"
LANGUAGE = "English"
ADAPTER_VERSION = "6"
TIMEOUT_SECONDS = 300
PAGE_DELAY_SECONDS = 0.25
MAX_PAGES = 500

# Pilot 008 accepted this exact bounded-wildcard source translation.
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "ce39aeee6c901324a16a588fc368a92ac1f3b5bb15a19705dcb2b8aa7c24a348"
)
EXPECTED_TERM_SNAPSHOT_SHA256 = (
    "7ab4c27fe49bd1bfa9c45600a669896b507fc08055045128b6212a6ee407193f"
)
EXPECTED_PILOT_ASSESSMENT_SHA256 = (
    "693ee8e8dca2c4e31607644c65e22fb153ed2cd30754fdfe4b1752cf31ffce99"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_text(value: str) -> str:
    return digest_bytes(value.encode("utf-8"))


def digest_ids(values: Sequence[str] | set[str]) -> str:
    hasher = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "big"))
        hasher.update(encoded)
    return hasher.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def encoded_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_new_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(value)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:  # pragma: no cover - OS write invariant
                raise OSError(f"Could not write {path}")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    write_new_bytes(path, encoded_json(value))


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def load_queries() -> Any:
    require_regular(QUERY_SNAPSHOT)
    require_regular(TERM_SNAPSHOT)
    if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
        raise RuntimeError("The accepted ATAI bounded-wildcard query snapshot changed")
    if digest(TERM_SNAPSHOT) != EXPECTED_TERM_SNAPSHOT_SHA256:
        raise RuntimeError("The ATAI ordinary-term snapshot changed")
    specification = importlib.util.spec_from_file_location(
        "atai_final_direct_queries", QUERY_SNAPSHOT
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    if tuple(module.SCHEDULE_IDS) != PARTITIONS:
        raise RuntimeError("The accepted ATAI partition schedule changed")
    if tuple(module.WILDCARD_SCHEDULE) != PARTITIONS:
        raise RuntimeError("The ATAI wildcard query order changed")
    if module.FAMILY_COUNT != 128 or module.REPLACED_TERM_COUNT != 292:
        raise RuntimeError("The accepted ATAI wildcard family map changed")
    return module


def adapter_version() -> str:
    require_regular(ADAPTER)
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot determine the ATAI adapter version")
    return match.group(1)


def bindings() -> dict[str, str]:
    paths = (
        SCRIPT_PATH,
        QUERY_SNAPSHOT,
        TERM_SNAPSHOT,
        PILOT_ASSESSMENT,
        SOURCE_GUIDELINE,
        MAIN_PROTOCOL,
        DISCOVERY_PROTOCOL,
    )
    for path in paths:
        require_regular(path)
    return {relative(path): digest(path) for path in paths}


def output_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return output_dir / str(event["output_filename"])


def screenshot_paths(path: Path) -> dict[str, Path]:
    return {
        "search_page": path.with_name(f"{path.stem}.search-page.png"),
        "results_page": path.with_name(f"{path.stem}.results-page.png"),
    }


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ATAI_COMMIT.json")


def failure_path(output_dir: Path, event: Mapping[str, Any]) -> Path:
    return (
        output_dir
        / "failures"
        / str(event["event_id"])
        / f"{event['partition_id']}.NON_MERGEABLE_FAILURE.json"
    )


def plan_event(
    partition: str, query: str, strategy_version: str, *, sequence: int
) -> dict[str, Any]:
    output = f"{partition}.json"
    event_suffix = "001" if sequence == 1 else f"r{sequence:03d}"
    return {
        "event_id": f"final-main-{partition}-atai-{event_suffix}",
        "partition_id": partition,
        "query": query,
        "query_sha256": digest_text(query),
        "query_characters": len(query),
        "bounded_wildcard_operator_count": query.count("[*"),
        "output_filename": output,
        "screenshot_filenames": {
            "search_page": f"{partition}.search-page.png",
            "results_page": f"{partition}.results-page.png",
        },
        "date_start": DATE_START,
        "date_end": DATE_END,
        "language": LANGUAGE,
        "max_pages": MAX_PAGES,
        "timeout_seconds": TIMEOUT_SECONDS,
        "page_delay_seconds": PAGE_DELAY_SECONDS,
        "require_complete": True,
        "strict_passes": 2,
        "full_abstracts": True,
        "source_publication_types": True,
        "strategy_version": strategy_version,
    }


def build_plan(
    *,
    sequence: int = 1,
    superseded_plan: Path | None = None,
    superseded_receipt: Path | None = None,
    selected_partitions: Sequence[str] | None = None,
) -> dict[str, Any]:
    if sequence < 1:
        raise ValueError("Final-run sequence must be positive")
    partitions = (
        PARTITIONS
        if selected_partitions is None
        else tuple(dict.fromkeys(selected_partitions))
    )
    if not partitions or partitions != tuple(
        partition for partition in PARTITIONS if partition in partitions
    ):
        raise ValueError("Selected partitions must be a nonempty canonical subset")
    if sequence == 1 and partitions != PARTITIONS:
        raise ValueError("The first final plan must declare every partition")
    if sequence > 1 and (superseded_plan is None or superseded_receipt is None):
        raise ValueError("A corrective plan requires the superseded plan and receipt")
    failed_partitions: tuple[str, ...] = ()
    inherited_strategy_version: str | None = None
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        require_regular(superseded_plan)
        require_regular(superseded_receipt)
        prior_plan = load(superseded_plan)
        inherited = prior_plan.get("strategy_version")
        if (
            not isinstance(inherited, str)
            or re.fullmatch(r"[0-9a-f]{40}", inherited) is None
        ):
            raise ValueError("The superseded plan has no valid strategy version")
        inherited_strategy_version = inherited
        prior_receipt = load(superseded_receipt)
        prior_outcomes = prior_receipt.get("outcomes")
        if not isinstance(prior_outcomes, list):
            raise ValueError("The superseded receipt has no outcome list")
        failed_partitions = tuple(
            str(outcome.get("partition_id"))
            for outcome in prior_outcomes
            if isinstance(outcome, Mapping) and outcome.get("success") is not True
        )
        if partitions not in {PARTITIONS, failed_partitions}:
            raise ValueError(
                "A corrective plan must rerun all partitions or exactly the failed subset"
            )
    queries = load_queries()
    if adapter_version() != ADAPTER_VERSION:
        raise RuntimeError(f"The ATAI final run requires adapter v{ADAPTER_VERSION}")
    require_regular(PILOT_ASSESSMENT)
    if digest(PILOT_ASSESSMENT) != EXPECTED_PILOT_ASSESSMENT_SHA256:
        raise RuntimeError("The accepted ATAI Pilot 008 assessment changed")
    repository_revision = repository_head()
    strategy_version = inherited_strategy_version or repository_revision
    events = [
        plan_event(
            partition,
            queries.WILDCARD_SCHEDULE[partition],
            strategy_version,
            sequence=sequence,
        )
        for partition in partitions
    ]
    plan = {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "repository_head_at_predeclaration": repository_revision,
        "final_run_sequence": sequence,
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "review_id": REVIEW_ID,
        "event_kind": "final",
        "phase": PHASE,
        "strategy_reference": STRATEGY_REFERENCE,
        "strategy_version": strategy_version,
        "concept_schedule_commit": queries.PROTOCOL_COMMIT,
        "accepted_translation_snapshot": relative(QUERY_SNAPSHOT),
        "accepted_translation_snapshot_sha256": digest(QUERY_SNAPSHOT),
        "ordinary_term_snapshot": relative(TERM_SNAPSHOT),
        "ordinary_term_snapshot_sha256": digest(TERM_SNAPSHOT),
        "readiness_evidence": {
            "pilot": "008",
            "assessment": relative(PILOT_ASSESSMENT),
            "assessment_sha256": digest(PILOT_ASSESSMENT),
            "decision": "accept_bounded_wildcard_translation",
        },
        "cutoff": {
            "exact_common_cutoff": DATE_END,
            "source_date_start": DATE_START,
            "source_date_end_inclusive": DATE_END,
            "date_basis": "publication",
            "source_precision": "calendar_day",
        },
        "source_configuration": {
            "source_or_collection": SOURCE,
            "interface": "ProQuest Command Line Search",
            "platform": "ProQuest Platform",
            "url": "https://www.proquest.com/ataindex/commandline",
            "database_selection": [SOURCE],
            "fields": ["NOFT", "IF.EXACT"],
            "language_clause": "LA(English)",
            "publication_type_filter": None,
            "peer_review_filter": None,
            "full_text_filter": None,
            "access_filter": None,
            "controlled_vocabulary_supplement": None,
            "spelling_variants": False,
            "form_variants": False,
            "show_expansions": False,
            "sort": "DateAsc",
            "page_size": 20,
        },
        "record_capture_contract": {
            "full_abstracts": {
                "required": True,
                "normalized_field": "abstract",
                "native_source": "ProQuest normal Abstract/Details route",
                "require_nonempty_for_each_record": True,
                "require_abstract_not_available_false": True,
                "snippet_substitution": False,
            },
            "source_publication_types": {
                "required": True,
                "normalized_field": "documentType",
                "native_source": "ProQuest rendered result-card source type",
                "require_nonempty_for_each_record": True,
                "source_filter_applied": None,
                "reviewer_coding": "Do not infer screening publication_type from source metadata.",
            },
        },
        "translation": {
            "literal_atom": "(NOFT(L(s)) OR IF.EXACT(L(s)))",
            "bounded_family_atom": "NOFT(W(V)) OR every replaced IF.EXACT literal",
            "wildcard_scope": "NOFT only. Keep exact IF alternatives literal.",
            "wildcard_family_count": queries.FAMILY_COUNT,
            "replaced_literal_occurrence_count": queries.REPLACED_TERM_COUNT,
            "wildcard_families": queries.FAMILY_RECEIPTS,
            "wildcard_operators_by_block": queries.WILDCARD_OPERATOR_COUNT_BY_BLOCK,
            "query_sha256": {
                partition: digest_text(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "query_character_counts": {
                partition: len(queries.WILDCARD_SCHEDULE[partition])
                for partition in PARTITIONS
            },
            "wildcard_operators_by_partition": {
                partition: queries.WILDCARD_SCHEDULE[partition].count("[*")
                for partition in PARTITIONS
            },
            "proximity_operators": False,
            "pair_expansion": False,
            "query_splits": 0,
        },
        "strict_contract": {
            "required_complete_passes": 2,
            "membership_gate": "two stable complete rendered-result passes",
            "source_total_gate": "exact source total equals retained record count",
            "automatic_screenshots_required": True,
            "screenshot_opt_out": False,
            "full_abstracts_required": True,
            "source_publication_types_required": True,
        },
        "execution_policy": {
            "one_source_execution_per_partition": True,
            "continue_after_partition_failure": True,
            "retry_policy": "none after final-plan execution begins",
            "fresh_browser_per_partition": False,
            "skip_full_abstracts": False,
            "source_publication_type_capture": True,
        },
        "adapter": {
            "id": "search_proquest_aerospace",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
            "automatic_screenshots": True,
        },
        "bindings": {"files": bindings()},
        "partition_ids": list(partitions),
        "events": events,
    }
    if sequence > 1:
        assert superseded_plan is not None and superseded_receipt is not None
        targeted = partitions == failed_partitions and partitions != PARTITIONS
        plan["corrective_run"] = {
            "sequence": sequence,
            "reason": (
                "This corrective plan reruns exactly the source events that failed "
                "the superseded attempt. Selection uses only prior technical status."
                if targeted
                else "This corrective plan reruns every unchanged partition after "
                "the superseded attempt did not complete the full schedule."
            ),
            "selection_basis": (
                "prior_technical_failure_status_only"
                if targeted
                else "complete_unchanged_schedule_repetition"
            ),
            "failed_partitions_in_superseded_attempt": list(failed_partitions),
            "strategy_version_provenance": "inherited_from_superseded_plan",
            "superseded_plan": relative(superseded_plan),
            "superseded_plan_sha256": digest(superseded_plan),
            "superseded_run_receipt": relative(superseded_receipt),
            "superseded_run_receipt_sha256": digest(superseded_receipt),
        }
    return plan


def repository_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise RuntimeError("Cannot determine the repository revision")
    return value


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> list[str]:
    errors: list[str] = []
    queries = load_queries()
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("schema")
    sequence = plan.get("final_run_sequence", 1)
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        errors.append("sequence")
        sequence = 1
    corrective = plan.get("corrective_run")
    if sequence == 1:
        if corrective is not None:
            errors.append("unexpected_corrective")
    elif not isinstance(corrective, Mapping) or (
        corrective.get("sequence") != sequence
        or not isinstance(corrective.get("reason"), str)
        or not corrective.get("reason").strip()
        or not isinstance(corrective.get("superseded_plan"), str)
        or not isinstance(corrective.get("superseded_plan_sha256"), str)
        or not isinstance(corrective.get("superseded_run_receipt"), str)
        or not isinstance(corrective.get("superseded_run_receipt_sha256"), str)
    ):
        errors.append("corrective_provenance")
    else:
        superseded_plan = REPOSITORY_ROOT / corrective["superseded_plan"]
        superseded_receipt = REPOSITORY_ROOT / corrective["superseded_run_receipt"]
        if (
            not superseded_plan.is_file()
            or superseded_plan.is_symlink()
            or not superseded_receipt.is_file()
            or superseded_receipt.is_symlink()
            or digest(superseded_plan) != corrective["superseded_plan_sha256"]
            or digest(superseded_receipt) != corrective["superseded_run_receipt_sha256"]
        ):
            errors.append("corrective_binding")
    if (
        plan.get("source") != SOURCE
        or plan.get("source_id") != SOURCE_ID
        or plan.get("review_namespace") != REVIEW_NAMESPACE
        or plan.get("review_id") != REVIEW_ID
        or plan.get("event_kind") != "final"
        or plan.get("phase") != PHASE
        or plan.get("strategy_reference") != STRATEGY_REFERENCE
        or plan.get("concept_schedule_commit") != queries.PROTOCOL_COMMIT
        or plan.get("accepted_translation_snapshot") != relative(QUERY_SNAPSHOT)
        or plan.get("accepted_translation_snapshot_sha256") != digest(QUERY_SNAPSHOT)
        or plan.get("ordinary_term_snapshot") != relative(TERM_SNAPSHOT)
        or plan.get("ordinary_term_snapshot_sha256") != digest(TERM_SNAPSHOT)
    ):
        errors.append("identity")
    cutoff = plan.get("cutoff")
    if not isinstance(cutoff, Mapping) or (
        cutoff.get("exact_common_cutoff") != DATE_END
        or cutoff.get("source_date_start") != DATE_START
        or cutoff.get("source_date_end_inclusive") != DATE_END
        or cutoff.get("date_basis") != "publication"
        or cutoff.get("source_precision") != "calendar_day"
    ):
        errors.append("cutoff")
    readiness = plan.get("readiness_evidence")
    if not isinstance(readiness, Mapping) or (
        readiness.get("pilot") != "008"
        or readiness.get("assessment") != relative(PILOT_ASSESSMENT)
        or readiness.get("assessment_sha256") != digest(PILOT_ASSESSMENT)
        or readiness.get("decision") != "accept_bounded_wildcard_translation"
    ):
        errors.append("readiness")
    configuration = plan.get("source_configuration")
    expected_configuration = {
        "source_or_collection": SOURCE,
        "interface": "ProQuest Command Line Search",
        "platform": "ProQuest Platform",
        "url": "https://www.proquest.com/ataindex/commandline",
        "database_selection": [SOURCE],
        "fields": ["NOFT", "IF.EXACT"],
        "language_clause": "LA(English)",
        "publication_type_filter": None,
        "peer_review_filter": None,
        "full_text_filter": None,
        "access_filter": None,
        "controlled_vocabulary_supplement": None,
        "spelling_variants": False,
        "form_variants": False,
        "show_expansions": False,
        "sort": "DateAsc",
        "page_size": 20,
    }
    if not isinstance(configuration, Mapping) or any(
        configuration.get(key) != value for key, value in expected_configuration.items()
    ):
        errors.append("source_configuration")
    capture = plan.get("record_capture_contract")
    if not isinstance(capture, Mapping) or (
        capture.get("full_abstracts", {}).get("required") is not True
        or capture.get("full_abstracts", {}).get("normalized_field") != "abstract"
        or capture.get("full_abstracts", {}).get("require_nonempty_for_each_record")
        is not True
        or capture.get("full_abstracts", {}).get("require_abstract_not_available_false")
        is not True
        or capture.get("full_abstracts", {}).get("snippet_substitution") is not False
        or capture.get("source_publication_types", {}).get("required") is not True
        or capture.get("source_publication_types", {}).get("normalized_field")
        != "documentType"
        or capture.get("source_publication_types", {}).get(
            "require_nonempty_for_each_record"
        )
        is not True
        or capture.get("source_publication_types", {}).get("source_filter_applied")
        is not None
    ):
        errors.append("record_capture_contract")
    translation = plan.get("translation")
    if not isinstance(translation, Mapping) or (
        translation.get("wildcard_family_count") != 128
        or translation.get("replaced_literal_occurrence_count") != 292
        or translation.get("wildcard_families") != queries.FAMILY_RECEIPTS
        or translation.get("wildcard_operators_by_block")
        != queries.WILDCARD_OPERATOR_COUNT_BY_BLOCK
        or translation.get("proximity_operators") is not False
        or translation.get("pair_expansion") is not False
        or translation.get("query_splits") != 0
    ):
        errors.append("translation")
    strict = plan.get("strict_contract")
    if not isinstance(strict, Mapping) or (
        strict.get("required_complete_passes") != 2
        or strict.get("automatic_screenshots_required") is not True
        or strict.get("screenshot_opt_out") is not False
        or strict.get("full_abstracts_required") is not True
        or strict.get("source_publication_types_required") is not True
    ):
        errors.append("strict_contract")
    policy = plan.get("execution_policy")
    if not isinstance(policy, Mapping) or (
        policy.get("one_source_execution_per_partition") is not True
        or policy.get("continue_after_partition_failure") is not True
        or policy.get("retry_policy") != "none after final-plan execution begins"
        or policy.get("skip_full_abstracts") is not False
        or policy.get("source_publication_type_capture") is not True
    ):
        errors.append("execution_policy")
    adapter = plan.get("adapter")
    if not isinstance(adapter, Mapping) or (
        adapter.get("id") != "search_proquest_aerospace"
        or adapter.get("version") != ADAPTER_VERSION
        or adapter.get("version") != adapter_version()
        or adapter.get("sha256") != digest(ADAPTER)
        or adapter.get("automatic_screenshots") is not True
    ):
        errors.append("adapter")
    raw_partitions = plan.get("partition_ids")
    plan_partitions = (
        tuple(raw_partitions)
        if isinstance(raw_partitions, list)
        and all(isinstance(value, str) for value in raw_partitions)
        else ()
    )
    if not plan_partitions or plan_partitions != tuple(
        partition for partition in PARTITIONS if partition in plan_partitions
    ):
        errors.append("partitions")
        plan_partitions = PARTITIONS
    if sequence == 1 and plan_partitions != PARTITIONS:
        errors.append("initial_partition_coverage")
    if sequence > 1 and isinstance(corrective, Mapping):
        prior_receipt_path = REPOSITORY_ROOT / str(
            corrective.get("superseded_run_receipt", "")
        )
        if prior_receipt_path.is_file():
            prior_outcomes = load(prior_receipt_path).get("outcomes")
            failed = (
                tuple(
                    str(outcome.get("partition_id"))
                    for outcome in prior_outcomes
                    if isinstance(outcome, Mapping)
                    and outcome.get("success") is not True
                )
                if isinstance(prior_outcomes, list)
                else ()
            )
            if plan_partitions not in {PARTITIONS, failed}:
                errors.append("corrective_partition_selection")
            if corrective.get("failed_partitions_in_superseded_attempt") not in (
                None,
                list(failed),
            ):
                errors.append("corrective_failed_partition_receipt")
    events = plan.get("events")
    if not isinstance(events, list) or len(events) != len(plan_partitions):
        errors.append("events")
        events = []
    strategy_version = plan.get("strategy_version")
    if (
        not isinstance(strategy_version, str)
        or re.fullmatch(r"[0-9a-f]{40}", strategy_version) is None
    ):
        errors.append("strategy_version")
        strategy_version = ""
    for event, partition in zip(events, plan_partitions, strict=False):
        if not isinstance(event, Mapping):
            errors.append(f"event:{partition}")
            continue
        expected = plan_event(
            partition,
            queries.WILDCARD_SCHEDULE[partition],
            strategy_version,
            sequence=sequence,
        )
        fields = tuple(expected)
        if any(event.get(field) != expected[field] for field in fields):
            errors.append(f"event:{partition}")
        query = event.get("query")
        if (
            not isinstance(query, str)
            or "NEAR" in query.upper()
            or " PRE/" in query.upper()
        ):
            errors.append(f"query_syntax:{partition}")
    if verify_bindings:
        files = plan.get("bindings", {}).get("files", {})
        if not isinstance(files, Mapping):
            errors.append("bindings")
        else:
            for name, expected_hash in files.items():
                path = REPOSITORY_ROOT / str(name)
                if (
                    not path.is_file()
                    or path.is_symlink()
                    or digest(path) != expected_hash
                ):
                    errors.append(f"binding:{name}")
    return errors


def command_for(
    event: Mapping[str, Any], staged_output: Path, plan: Mapping[str, Any]
) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(event["query"]),
        "--date-start",
        str(event["date_start"]),
        "--date-end",
        str(event["date_end"]),
        "--date-basis",
        "publication",
        "--language",
        str(event["language"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--require-complete",
        "--output-path",
        str(staged_output),
        "--prisma-run-id",
        str(event["event_id"]),
        "--prisma-review-id",
        str(plan["review_id"]),
        "--prisma-strategy-reference",
        str(plan["strategy_reference"]),
        "--prisma-strategy-version",
        str(event["strategy_version"]),
        "--prisma-phase",
        str(plan["phase"]),
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        f"ATAI {event['partition_id']}",
        "--prisma-partition-description",
        f"Final ATAI direct discovery partition {event['partition_id']}.",
    ]


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "file_name": path.name,
        "sha256": digest(path),
        "bytes": path.stat().st_size,
    }


def capture_summary(rows: Sequence[Any]) -> dict[str, Any]:
    abstracts = 0
    blank_abstracts = 0
    unavailable_abstracts = 0
    source_types: Counter[str] = Counter()
    missing_source_types = 0
    stable_ids: list[str] = []
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            errors.append(f"record_{index}_not_object")
            continue
        paper_id = row.get("paperId")
        if not isinstance(paper_id, str) or not paper_id.isdigit():
            errors.append(f"record_{index}_invalid_paper_id")
        else:
            stable_ids.append(paper_id)
        abstract = row.get("abstract")
        if isinstance(abstract, str) and abstract.strip():
            abstracts += 1
        else:
            blank_abstracts += 1
            errors.append(f"record_{index}_blank_abstract")
        if row.get("abstract_not_available") is not False:
            unavailable_abstracts += 1
            errors.append(f"record_{index}_abstract_not_proven_available")
        document_type = row.get("documentType")
        if isinstance(document_type, str) and document_type.strip():
            source_types[document_type.strip()] += 1
        else:
            missing_source_types += 1
            errors.append(f"record_{index}_missing_source_publication_type")
    if len(stable_ids) != len(set(stable_ids)):
        errors.append("duplicate_stable_id_within_partition")
    return {
        "records": len(rows),
        "stable_ids": stable_ids,
        "stable_id_set_sha256": digest_ids(set(stable_ids)),
        "full_abstract_count": abstracts,
        "blank_abstract_count": blank_abstracts,
        "source_abstract_not_available_count": unavailable_abstracts,
        "source_publication_type_count": sum(source_types.values()),
        "missing_source_publication_type_count": missing_source_types,
        "source_publication_type_counts": dict(sorted(source_types.items())),
        "valid": not errors,
        "errors": errors,
    }


def controls_summary(
    artifact: Mapping[str, Any], event: Mapping[str, Any], plan: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    metadata = artifact.get("output_metadata")
    if not isinstance(metadata, Mapping):
        return ["missing_output_metadata"]
    run = metadata.get("prisma_search_run")
    if not isinstance(run, Mapping):
        return ["missing_prisma_search_run"]
    strategy = run.get("strategy")
    if not isinstance(strategy, Mapping):
        return ["missing_prisma_strategy"]
    limits = strategy.get("limits")
    if not isinstance(limits, Mapping):
        return ["missing_prisma_limits"]
    descriptor = run.get("source_descriptor")
    if not isinstance(descriptor, Mapping) or (
        descriptor.get("source_id") != SOURCE_ID
        or descriptor.get("source_label") != SOURCE
        or descriptor.get("database_name") != SOURCE
        or descriptor.get("resource_name") != SOURCE
    ):
        errors.append("source_descriptor")
    adapter = run.get("adapter")
    expected_adapter = plan.get("adapter", {})
    if not isinstance(adapter, Mapping) or (
        adapter.get("adapter_id") != "search_proquest_aerospace"
        or adapter.get("adapter_version") != ADAPTER_VERSION
        or adapter.get("script_sha256") != expected_adapter.get("sha256")
    ):
        errors.append("adapter")
    coverage = run.get("coverage")
    if not isinstance(coverage, Mapping) or (
        coverage.get("coverage_scope") != "partition"
        or coverage.get("partition_id") != event["partition_id"]
    ):
        errors.append("coverage")
    if (
        run.get("run_id") != event["event_id"]
        or run.get("review_id") != plan["review_id"]
        or run.get("strategy_reference") != plan["strategy_reference"]
        or run.get("strategy_version") != event["strategy_version"]
        or run.get("phase") != plan["phase"]
        or run.get("report_ready") is not True
    ):
        errors.append("provenance")
    if (
        strategy.get("requested_query") != event["query"]
        or strategy.get("search_scope") != SOURCE
        or strategy.get("query_syntax", {}).get("spelling_variants") is not False
        or strategy.get("query_syntax", {}).get("form_variants") is not False
        or strategy.get("query_syntax", {}).get("show_variants") is not False
        or strategy.get("sort", {}).get("value") != "DateAsc"
    ):
        errors.append("strategy")
    language = limits.get("language", {})
    publication_date = limits.get("publication_date", {})
    effective_date = (
        publication_date.get("effective", {})
        if isinstance(publication_date, Mapping)
        else {}
    )
    if (
        not isinstance(language, Mapping)
        or language.get("state") != "applied"
        or language.get("value") != "LA(English)"
        or not isinstance(effective_date, Mapping)
        or effective_date.get("basis") != "publication"
        or effective_date.get("start") != DATE_START
        or effective_date.get("end") != DATE_END
        or effective_date.get("inclusive") != "both"
    ):
        errors.append("date_or_language")
    for name, expected_state in (
        ("document_type", "not_applied"),
        ("peer_reviewed", "not_applied"),
        ("exclude_wire_feeds", "not_applied"),
        ("source_type", "not_applied"),
        ("publication_title", "not_applied"),
        ("full_text", "unavailable"),
        ("access", "unavailable"),
    ):
        value = limits.get(name, {})
        if not isinstance(value, Mapping) or value.get("state") != expected_state:
            errors.append(f"limit:{name}")
    counts = run.get("staged_counts")
    if not isinstance(counts, Mapping) or (
        counts.get("source_reported_total") != artifact.get("total")
        or counts.get("source_reported_total_exact") is not True
        or counts.get("raw_source_records") != artifact.get("total")
        or counts.get("client_side_exclusions") != 0
        or counts.get("within_source_duplicates_removed") != 0
        or counts.get("malformed_records_dropped") != 0
    ):
        errors.append("staged_counts")
    return errors


def screenshot_summary(
    artifact: Mapping[str, Any], path: Path
) -> tuple[list[dict[str, Any]], list[str]]:
    metadata = artifact.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    receipt = metadata.get("screenshots")
    receipt = receipt if isinstance(receipt, Mapping) else {}
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    if (
        receipt.get("schema_version") != "atai-automatic-screenshots/v1"
        or receipt.get("automatic") is not True
        or receipt.get("same_directory_as_json") is not True
    ):
        errors.append("screenshot_receipt")
    for kind, screenshot in screenshot_paths(path).items():
        evidence = receipt.get(kind)
        evidence = evidence if isinstance(evidence, Mapping) else {}
        valid = (
            screenshot.is_file()
            and not screenshot.is_symlink()
            and screenshot.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
            and evidence.get("path") == screenshot.name
            and evidence.get("sha256") == digest(screenshot)
            and isinstance(evidence.get("width"), int)
            and evidence["width"] > 0
            and isinstance(evidence.get("height"), int)
            and evidence["height"] > 0
            and evidence.get("browser_chrome_captured") is False
            and evidence.get("complete_page_url_retained") is False
            and evidence.get("session_identifiers_retained") is False
        )
        if not valid:
            errors.append(f"screenshot:{kind}")
        summaries.append(
            {
                "kind": kind,
                "path": screenshot.name,
                "sha256": digest(screenshot) if screenshot.is_file() else None,
                "valid": valid,
            }
        )
    return summaries, errors


def artifact_summary(
    path: Path,
    event: Mapping[str, Any],
    plan: Mapping[str, Any],
    *,
    require_marker: bool,
) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {
            "artifact_written": False,
            "valid": False,
            "error_stage": "missing_output",
        }
    try:
        artifact = load(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {"artifact_written": True, "valid": False, "error_stage": "invalid_json"}
    errors: list[str] = []
    rows = artifact.get("results")
    if not isinstance(rows, list):
        rows = []
        errors.append("missing_results")
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("source") != SOURCE
        or artifact.get("requested_query") != event["query"]
        or not isinstance(artifact.get("executed_query"), str)
        or not artifact["executed_query"].endswith(" AND LA(English)")
        or not isinstance(artifact.get("total"), int)
        or artifact["total"] < 0
        or artifact["total"] != len(rows)
    ):
        errors.append("artifact_shape")
    metadata = artifact.get("output_metadata")
    if not isinstance(metadata, Mapping) or (
        metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("count_only") is not False
        or metadata.get("merge_eligible") is not True
        or metadata.get("normalized_merge_eligible") not in {None, True}
        or artifact.get("do_not_merge") is True
    ):
        errors.append("completion")
    captures = capture_summary(rows)
    if not captures["valid"]:
        errors.append("record_capture")
    control_errors = controls_summary(artifact, event, plan)
    errors.extend(control_errors)
    screenshots, screenshot_errors = screenshot_summary(artifact, path)
    errors.extend(screenshot_errors)
    marker = marker_path(path)
    marker_valid: bool | None = None
    if require_marker:
        marker_valid = validate_marker(marker, path, event, captures, screenshots)
        if not marker_valid:
            errors.append("commit_marker")
    return {
        "artifact_written": True,
        "valid": not errors,
        "artifact_sha256": digest(path),
        "artifact_bytes": path.stat().st_size,
        "status": metadata.get("status") if isinstance(metadata, Mapping) else None,
        "total": artifact.get("total"),
        "stable_id_count": len(captures["stable_ids"]),
        "stable_id_set_sha256": captures["stable_id_set_sha256"],
        "controls_valid": not control_errors,
        "screenshots_valid": not screenshot_errors,
        "terminal_marker_valid": marker_valid,
        "record_capture": captures,
        "screenshots": screenshots,
        "validation_errors": errors,
    }


def marker_payload(
    output: Path,
    event: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    captures = summary["record_capture"]
    return {
        "schema_version": MARKER_SCHEMA,
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "query_sha256": event["query_sha256"],
        "normalized_json": file_receipt(output),
        "screenshots": [
            file_receipt(screenshot) for screenshot in screenshot_paths(output).values()
        ],
        "record_capture": {
            "records": captures["records"],
            "stable_id_set_sha256": captures["stable_id_set_sha256"],
            "full_abstract_count": captures["full_abstract_count"],
            "blank_abstract_count": captures["blank_abstract_count"],
            "source_abstract_not_available_count": captures[
                "source_abstract_not_available_count"
            ],
            "source_publication_type_count": captures["source_publication_type_count"],
            "missing_source_publication_type_count": captures[
                "missing_source_publication_type_count"
            ],
            "source_publication_type_counts": captures[
                "source_publication_type_counts"
            ],
        },
    }


def validate_marker(
    marker: Path,
    output: Path,
    event: Mapping[str, Any],
    captures: Mapping[str, Any],
    screenshots: Sequence[Mapping[str, Any]],
) -> bool:
    if not marker.is_file() or marker.is_symlink():
        return False
    try:
        value = load(marker)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    expected = marker_payload(
        output,
        event,
        {"record_capture": captures, "screenshots": list(screenshots)},
    )
    return value == expected


def publish_file_no_replace(source: Path, destination: Path) -> None:
    if not source.is_file() or source.is_symlink():
        raise OSError(f"Missing staged artifact: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination, follow_symlinks=False)
    except FileExistsError:
        raise
    except OSError:
        # The stage and destination share a parent in normal use. Retain a
        # create-only fallback for filesystems that reject hard links.
        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        try:
            with source.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    os.write(descriptor, chunk)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    source.unlink()


def publish_staged_success(stage: Path, output: Path) -> None:
    # Publish the mergeable JSON after its required screenshots. The terminal
    # marker remains the final commit witness.
    destinations = [*screenshot_paths(output).values(), output]
    sources = [*screenshot_paths(stage).values(), stage]
    if any(path.exists() or path.is_symlink() for path in destinations):
        raise FileExistsError(
            f"Refusing to overwrite final ATAI artifacts for {output.name}"
        )
    for source, destination in zip(sources, destinations, strict=True):
        publish_file_no_replace(source, destination)


def quarantine_staged_artifact(stage: Path, reason: str) -> None:
    """Make an unaccepted staged source artifact visibly nonmergeable."""
    if not stage.is_file() or stage.is_symlink():
        return
    artifact = load(stage)
    metadata = artifact.setdefault("output_metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("A staged ATAI artifact has invalid output metadata")
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["non_mergeable_reason"] = reason
    artifact["do_not_merge"] = True
    run = metadata.get("prisma_search_run")
    if isinstance(run, dict):
        run["report_ready"] = False
        reasons = run.get("report_readiness_reasons")
        if not isinstance(reasons, list):
            reasons = []
        if "retained_failed_final_attempt" not in reasons:
            reasons.append("retained_failed_final_attempt")
        run["report_readiness_reasons"] = reasons
    stage.write_bytes(encoded_json(artifact))


def preserve_staged_failure(stage: Path, destination: Path) -> Path | None:
    if not stage.is_file() or stage.is_symlink():
        return None
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged_screenshots = screenshot_paths(stage)
    destinations = {
        kind: destination.parent / screenshot.name
        for kind, screenshot in staged_screenshots.items()
    }
    if any(path.exists() or path.is_symlink() for path in destinations.values()):
        raise FileExistsError("Refusing to overwrite retained ATAI failure screenshots")
    publish_file_no_replace(stage, destination)
    for kind, screenshot in staged_screenshots.items():
        if screenshot.is_file() and not screenshot.is_symlink():
            publish_file_no_replace(screenshot, destinations[kind])
    return destination


def safe_source_error(stderr: str) -> str | None:
    """Retain one short source error line without local or browser context."""
    for line in stderr.splitlines():
        value = line.strip()
        if not value.startswith("Error: "):
            continue
        value = value.removeprefix("Error: ").strip()
        if (
            value
            and len(value) <= 500
            and not re.search(
                r"(?:https?://|file:|/Users/|/tmp/|127\\.0\\.0\\.1)", value
            )
        ):
            return value
    return None


def run_final(
    plan_path: Path, output_dir: Path, receipt_path: Path, settle_seconds: float
) -> int:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {receipt_path}")
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    if errors:
        raise ValueError("Invalid ATAI final plan: " + ", ".join(errors))
    if output_dir.is_symlink():
        raise ValueError("The ATAI final output directory cannot be a symlink")
    output_dir.mkdir(parents=True, exist_ok=True)
    if not SOURCE_UNION_TOOL.is_file():
        raise FileNotFoundError(f"Missing source-union tool: {SOURCE_UNION_TOOL}")

    started = now()
    outcomes: list[dict[str, Any]] = []
    for position, event in enumerate(plan["events"]):
        if position and settle_seconds:
            import time

            time.sleep(settle_seconds)
        output = output_path(output_dir, event)
        final_entries = [
            output,
            marker_path(output),
            *screenshot_paths(output).values(),
        ]
        if any(path.exists() or path.is_symlink() for path in final_entries):
            raise FileExistsError(
                f"Refusing to overwrite final ATAI artifacts for {event['partition_id']}"
            )
        stage_directory = Path(
            tempfile.mkdtemp(prefix=".atai-final-stage-", dir=output_dir)
        )
        staged_output = stage_directory / output.name
        stdout = ""
        stderr = ""
        exit_code: int | None = None
        summary: dict[str, Any] = {}
        published = False
        failure_artifact: Path | None = None
        try:
            completed = subprocess.run(
                command_for(event, staged_output, plan),
                check=False,
                capture_output=True,
                text=True,
                timeout=int(event["timeout_seconds"]) * 2 + 120,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            exit_code = completed.returncode
            summary = artifact_summary(staged_output, event, plan, require_marker=False)
            if exit_code == 0 and summary.get("valid") is True:
                publish_staged_success(staged_output, output)
                marker = marker_path(output)
                write_new_json(marker, marker_payload(output, event, summary))
                summary = artifact_summary(output, event, plan, require_marker=True)
                published = summary.get("valid") is True
            else:
                quarantine_staged_artifact(
                    staged_output,
                    "The final ATAI event was not accepted by its predeclared run contract.",
                )
                failure_artifact = preserve_staged_failure(
                    staged_output, failure_path(output_dir, event)
                )
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout if isinstance(error.stdout, str) else ""
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            summary = {
                "artifact_written": staged_output.is_file(),
                "valid": False,
                "error_stage": "subprocess_timeout",
            }
            quarantine_staged_artifact(
                staged_output,
                "The final ATAI event exceeded the predeclared local execution timeout.",
            )
            failure_artifact = preserve_staged_failure(
                staged_output, failure_path(output_dir, event)
            )
        finally:
            shutil.rmtree(stage_directory, ignore_errors=True)
        outcome = {
            "event_id": event["event_id"],
            "partition_id": event["partition_id"],
            "success": published,
            "artifact": output.name if published else None,
            "failure_artifact": (
                relative(failure_artifact) if failure_artifact is not None else None
            ),
            "exit_code": exit_code,
            "attempt_count": 1,
            "stdout_sha256": digest_text(stdout),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "stderr_sha256": digest_text(stderr),
            "stderr_bytes": len(stderr.encode("utf-8")),
            "source_error": safe_source_error(stderr),
            **summary,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "partition": event["partition_id"],
                    "success": published,
                    "exit_code": exit_code,
                    "total": outcome.get("total"),
                    "full_abstracts": outcome.get("record_capture", {}).get(
                        "full_abstract_count"
                    ),
                    "source_publication_types": outcome.get("record_capture", {}).get(
                        "source_publication_type_count"
                    ),
                    "error_stage": outcome.get("error_stage"),
                }
            ),
            flush=True,
        )
    success = len(outcomes) == len(plan["events"]) and all(
        outcome.get("success") is True for outcome in outcomes
    )
    receipt = {
        "schema_version": RUN_SCHEMA,
        "source": plan["source"],
        "source_id": plan["source_id"],
        "review_namespace": plan["review_namespace"],
        "event_kind": "final",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "execution_policy": plan["execution_policy"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "planned_partition_count": len(plan["events"]),
        "attempted_partition_count": len(outcomes),
        "source_command_attempt_count": len(outcomes),
        "accepted_event_count": sum(
            outcome.get("success") is True for outcome in outcomes
        ),
        "all_partitions_attempted": len(outcomes) == len(plan["events"]),
        "success": success,
        "outcomes": outcomes,
    }
    write_new_json(receipt_path, receipt)
    return 0 if success else 1


def assess(
    plan_path: Path,
    receipt_path: Path,
    output_dir: Path,
    union_path: Path,
    assessment_path: Path,
) -> int:
    plan = load(plan_path)
    errors = validate_plan(plan, verify_bindings=True)
    receipt = load(receipt_path)
    if (
        receipt.get("schema_version") != RUN_SCHEMA
        or receipt.get("plan") != relative(plan_path)
        or receipt.get("plan_sha256") != digest(plan_path)
    ):
        errors.append("run_receipt")
    summaries: list[dict[str, Any]] = []
    inputs: list[Path] = []
    all_ids: set[str] = set()
    occurrence_count = 0
    for event in plan["events"]:
        path = output_path(output_dir, event)
        summary = artifact_summary(path, event, plan, require_marker=True)
        summaries.append(
            {"partition_id": event["partition_id"], "path": relative(path), **summary}
        )
        if summary.get("valid") is not True:
            errors.append(f"artifact:{event['partition_id']}")
            continue
        inputs.append(path)
        artifact = load(path)
        ids = {row["paperId"] for row in artifact["results"]}
        all_ids.update(ids)
        occurrence_count += len(ids)
    outcomes = receipt.get("outcomes")
    if receipt.get("success") is not True:
        errors.append("run_unsuccessful")
    if not isinstance(outcomes, list) or [
        outcome.get("partition_id")
        for outcome in outcomes
        if isinstance(outcome, Mapping)
    ] != list(PARTITIONS):
        errors.append("run_partition_coverage")
    elif any(outcome.get("success") is not True for outcome in outcomes):
        errors.append("run_event_failure")
    if not errors:
        if union_path.exists() or union_path.is_symlink():
            errors.append("source_union_destination_exists")
        else:
            command = [
                "uv",
                "run",
                str(SOURCE_UNION_TOOL),
                "--input",
                *[str(path) for path in inputs],
                "--output-path",
                str(union_path),
                "--expected-partitions",
                *PARTITIONS,
                "--expected-source",
                SOURCE_ID,
                "--review-namespace",
                REVIEW_NAMESPACE,
            ]
            completed = subprocess.run(
                command, check=False, capture_output=True, text=True
            )
            if completed.returncode != 0 or not union_path.is_file():
                errors.append("source_union_receipt")
    total_abstracts = sum(
        summary.get("record_capture", {}).get("full_abstract_count", 0)
        for summary in summaries
    )
    total_blank_abstracts = sum(
        summary.get("record_capture", {}).get("blank_abstract_count", 0)
        for summary in summaries
    )
    total_unavailable_abstracts = sum(
        summary.get("record_capture", {}).get("source_abstract_not_available_count", 0)
        for summary in summaries
    )
    source_types: Counter[str] = Counter()
    for summary in summaries:
        source_types.update(
            summary.get("record_capture", {}).get("source_publication_type_counts", {})
        )
    total_source_types = sum(source_types.values())
    missing_source_types = sum(
        summary.get("record_capture", {}).get(
            "missing_source_publication_type_count", 0
        )
        for summary in summaries
    )
    if total_blank_abstracts or total_unavailable_abstracts or missing_source_types:
        errors.append("record_capture_incomplete")
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": plan["source"],
        "source_id": plan["source_id"],
        "review_namespace": plan["review_namespace"],
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "run_receipt": relative(receipt_path),
        "run_receipt_sha256": digest(receipt_path),
        "adapter": plan["adapter"],
        "date_window": plan["cutoff"],
        "partition_count": len(summaries),
        "accepted_partition_count": sum(
            summary.get("valid") is True for summary in summaries
        ),
        "record_occurrence_count": occurrence_count,
        "unique_source_record_count": len(all_ids),
        "unique_source_record_id_set_sha256": digest_ids(all_ids),
        "full_abstract_occurrence_count": total_abstracts,
        "blank_abstract_occurrence_count": total_blank_abstracts,
        "source_abstract_not_available_occurrence_count": total_unavailable_abstracts,
        "source_publication_type_occurrence_count": total_source_types,
        "missing_source_publication_type_occurrence_count": missing_source_types,
        "source_publication_type_counts": dict(sorted(source_types.items())),
        "full_abstract_and_source_publication_type_capture_complete": bool(
            not errors
            and total_abstracts == occurrence_count
            and total_blank_abstracts == 0
            and total_unavailable_abstracts == 0
            and total_source_types == occurrence_count
            and missing_source_types == 0
        ),
        "source_union_receipt": relative(union_path) if union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path)
        if union_path.is_file()
        else None,
        "partitions": summaries,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new_json(assessment_path, assessment)
    return 0 if not errors else 1


def reconcile_attempts(
    plan_paths: Sequence[Path],
    receipt_paths: Sequence[Path],
    output_dir: Path,
    reconciled_path: Path,
    union_path: Path,
    assessment_path: Path,
) -> int:
    if len(plan_paths) != len(receipt_paths) or not plan_paths:
        raise ValueError(
            "Reconciliation requires matching nonempty plan and receipt lists"
        )
    for path in (reconciled_path, union_path, assessment_path):
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {path}")

    errors: list[str] = []
    selected: dict[
        str,
        tuple[dict[str, Any], dict[str, Any], Path, Path, dict[str, Any]],
    ] = {}
    attempt_receipts: list[dict[str, Any]] = []
    for plan_path, receipt_path in zip(plan_paths, receipt_paths, strict=True):
        require_regular(plan_path)
        require_regular(receipt_path)
        plan = load(plan_path)
        plan_errors = validate_plan(plan, verify_bindings=False)
        if plan_errors:
            errors.extend(f"plan:{plan_path.name}:{error}" for error in plan_errors)
        receipt = load(receipt_path)
        if (
            receipt.get("schema_version") != RUN_SCHEMA
            or receipt.get("plan") != relative(plan_path)
            or receipt.get("plan_sha256") != digest(plan_path)
        ):
            errors.append(f"receipt_binding:{receipt_path.name}")
        events = plan.get("events")
        events = events if isinstance(events, list) else []
        event_by_id = {
            str(event.get("event_id")): event
            for event in events
            if isinstance(event, dict)
        }
        outcomes = receipt.get("outcomes")
        outcomes = outcomes if isinstance(outcomes, list) else []
        if [
            outcome.get("event_id")
            for outcome in outcomes
            if isinstance(outcome, Mapping)
        ] != [event.get("event_id") for event in events]:
            errors.append(f"receipt_event_order:{receipt_path.name}")
        for outcome in outcomes:
            if not isinstance(outcome, dict) or outcome.get("success") is not True:
                continue
            event = event_by_id.get(str(outcome.get("event_id")))
            if event is None:
                errors.append(f"successful_event_missing_from_plan:{receipt_path.name}")
                continue
            partition = str(event.get("partition_id"))
            selected[partition] = (event, plan, plan_path, receipt_path, outcome)
        attempt_receipts.append(
            {
                "plan": relative(plan_path),
                "plan_sha256": digest(plan_path),
                "run_receipt": relative(receipt_path),
                "run_receipt_sha256": digest(receipt_path),
                "attempt_success": receipt.get("success") is True,
                "attempted_partition_count": receipt.get("attempted_partition_count"),
                "accepted_event_count": receipt.get("accepted_event_count"),
            }
        )

    if set(selected) != set(PARTITIONS):
        errors.append("incomplete_selected_partition_set")
    summaries: list[dict[str, Any]] = []
    selected_outcomes: list[dict[str, Any]] = []
    inputs: list[Path] = []
    all_ids: set[str] = set()
    occurrence_count = 0
    selected_strategy_pairs: set[tuple[str, str]] = set()
    for partition in PARTITIONS:
        selection = selected.get(partition)
        if selection is None:
            summaries.append(
                {
                    "partition_id": partition,
                    "path": relative(output_dir / f"{partition}.json"),
                    "artifact_written": False,
                    "valid": False,
                    "error_stage": "no_accepted_attempt",
                }
            )
            continue
        event, plan, plan_path, receipt_path, outcome = selection
        selected_strategy_pairs.add(
            (str(plan.get("strategy_reference")), str(event.get("strategy_version")))
        )
        path = output_path(output_dir, event)
        summary = artifact_summary(path, event, plan, require_marker=True)
        summaries.append({"partition_id": partition, "path": relative(path), **summary})
        if summary.get("valid") is not True:
            errors.append(f"artifact:{partition}")
            continue
        inputs.append(path)
        artifact = load(path)
        ids = {str(row["paperId"]) for row in artifact["results"]}
        all_ids.update(ids)
        occurrence_count += len(ids)
        selected_outcomes.append(
            {
                "partition_id": partition,
                "event_id": event["event_id"],
                "origin_plan": relative(plan_path),
                "origin_run_receipt": relative(receipt_path),
                "artifact": relative(path),
                "artifact_sha256": digest(path),
                "total": artifact["total"],
                "full_abstract_count": summary["record_capture"]["full_abstract_count"],
                "source_publication_type_count": summary["record_capture"][
                    "source_publication_type_count"
                ],
            }
        )
    if len(selected_strategy_pairs) != 1:
        errors.append("selected_strategy_identity_mismatch")

    if not errors:
        command = [
            "uv",
            "run",
            str(SOURCE_UNION_TOOL),
            "--input",
            *[str(path) for path in inputs],
            "--output-path",
            str(union_path),
            "--expected-partitions",
            *PARTITIONS,
            "--expected-source",
            SOURCE_ID,
            "--review-namespace",
            REVIEW_NAMESPACE,
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode != 0 or not union_path.is_file():
            errors.append("source_union_receipt")

    reconciled = {
        "schema_version": "slr1-atai-final-direct-run-reconciliation/v1",
        "status": "complete" if not errors else "failed",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "event_kind": "final",
        "strategy_reference": STRATEGY_REFERENCE,
        "attempt_count": len(attempt_receipts),
        "attempts": attempt_receipts,
        "expected_partitions": list(PARTITIONS),
        "selected_partition_count": len(selected_outcomes),
        "selected_outcomes": selected_outcomes,
        "source_union_receipt": relative(union_path) if union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path)
        if union_path.is_file()
        else None,
        "success": not errors,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new_json(reconciled_path, reconciled)

    total_abstracts = sum(
        summary.get("record_capture", {}).get("full_abstract_count", 0)
        for summary in summaries
    )
    total_blank_abstracts = sum(
        summary.get("record_capture", {}).get("blank_abstract_count", 0)
        for summary in summaries
    )
    total_unavailable_abstracts = sum(
        summary.get("record_capture", {}).get("source_abstract_not_available_count", 0)
        for summary in summaries
    )
    source_types: Counter[str] = Counter()
    for summary in summaries:
        source_types.update(
            summary.get("record_capture", {}).get("source_publication_type_counts", {})
        )
    total_source_types = sum(source_types.values())
    missing_source_types = sum(
        summary.get("record_capture", {}).get(
            "missing_source_publication_type_count", 0
        )
        for summary in summaries
    )
    if (
        total_abstracts != occurrence_count
        or total_blank_abstracts != 0
        or total_unavailable_abstracts != 0
        or total_source_types != occurrence_count
        or missing_source_types != 0
    ):
        errors.append("record_capture_incomplete")

    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "status": "passed" if not errors else "failed",
        "source": SOURCE,
        "source_id": SOURCE_ID,
        "review_namespace": REVIEW_NAMESPACE,
        "reconciled_run_receipt": relative(reconciled_path),
        "reconciled_run_receipt_sha256": digest(reconciled_path),
        "attempts": attempt_receipts,
        "date_window": {
            "source_date_start": DATE_START,
            "source_date_end_inclusive": DATE_END,
            "date_basis": "publication",
            "inclusive": "both",
        },
        "partition_count": len(summaries),
        "accepted_partition_count": sum(
            summary.get("valid") is True for summary in summaries
        ),
        "record_occurrence_count": occurrence_count,
        "unique_source_record_count": len(all_ids),
        "unique_source_record_id_set_sha256": digest_ids(all_ids),
        "full_abstract_occurrence_count": total_abstracts,
        "blank_abstract_occurrence_count": total_blank_abstracts,
        "source_abstract_not_available_occurrence_count": total_unavailable_abstracts,
        "source_publication_type_occurrence_count": total_source_types,
        "missing_source_publication_type_occurrence_count": missing_source_types,
        "source_publication_type_counts": dict(sorted(source_types.items())),
        "full_abstract_and_source_publication_type_capture_complete": bool(
            not errors
            and total_abstracts == occurrence_count
            and total_source_types == occurrence_count
        ),
        "source_union_receipt": relative(union_path) if union_path.is_file() else None,
        "source_union_receipt_sha256": digest(union_path)
        if union_path.is_file()
        else None,
        "partitions": summaries,
        "validation_errors": errors,
        "completed_at_utc": now(),
    }
    write_new_json(assessment_path, assessment)
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-plan")
    build_parser.add_argument("--output", type=Path, required=True)
    build_parser.add_argument("--sequence", type=int, default=1)
    build_parser.add_argument("--superseded-plan", type=Path)
    build_parser.add_argument("--superseded-receipt", type=Path)
    build_parser.add_argument(
        "--partition",
        action="append",
        choices=PARTITIONS,
        help="Corrective-only failed partition in canonical order (repeatable).",
    )

    check_parser = subparsers.add_parser("check-plan")
    check_parser.add_argument("--plan", type=Path, required=True)
    check_parser.add_argument("--verify-bindings", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=5.0)

    assess_parser = subparsers.add_parser("assess")
    assess_parser.add_argument("--plan", type=Path, required=True)
    assess_parser.add_argument("--receipt", type=Path, required=True)
    assess_parser.add_argument("--output-dir", type=Path, required=True)
    assess_parser.add_argument("--union-receipt", type=Path, required=True)
    assess_parser.add_argument("--assessment", type=Path, required=True)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument(
        "--attempt-plan", type=Path, action="append", required=True
    )
    reconcile_parser.add_argument(
        "--attempt-receipt", type=Path, action="append", required=True
    )
    reconcile_parser.add_argument("--output-dir", type=Path, required=True)
    reconcile_parser.add_argument("--reconciled-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--union-receipt", type=Path, required=True)
    reconcile_parser.add_argument("--assessment", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "build-plan":
        plan = build_plan(
            sequence=args.sequence,
            superseded_plan=args.superseded_plan,
            superseded_receipt=args.superseded_receipt,
            selected_partitions=args.partition,
        )
        errors = validate_plan(plan, verify_bindings=False)
        if errors:
            raise ValueError(
                "Generated an invalid ATAI final plan: " + ", ".join(errors)
            )
        write_new_json(args.output, plan)
        print(json.dumps({"saved": str(args.output), "events": len(plan["events"])}))
        return 0
    if args.command == "check-plan":
        errors = validate_plan(load(args.plan), verify_bindings=args.verify_bindings)
        print(json.dumps({"status": "ok" if not errors else "error", "errors": errors}))
        return 0 if not errors else 1
    if args.command == "run":
        if args.settle_seconds < 0:
            raise ValueError("--settle-seconds cannot be negative")
        return run_final(args.plan, args.output_dir, args.receipt, args.settle_seconds)
    if args.command == "assess":
        return assess(
            args.plan,
            args.receipt,
            args.output_dir,
            args.union_receipt,
            args.assessment,
        )
    if args.command == "reconcile":
        return reconcile_attempts(
            args.attempt_plan,
            args.attempt_receipt,
            args.output_dir,
            args.reconciled_receipt,
            args.union_receipt,
            args.assessment,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
