#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Run the read-only Scopus adapter with a longer passive editor readback.

This is a Pilot 003 recovery harness, not a forked adapter.  It imports the
pinned read-only adapter and changes only the maximum passive interval after
ordinary key entry before it gives up on Monaco's EditContext.  Search remains
unsubmitted until exact native readback succeeds; no source interaction is
replayed and the repaired native abstract follow-up remains the one in the
pinned adapter.
"""

from __future__ import annotations

import importlib.util
import sys

from adapter_paths import configured_adapter_path


REFERENCE_ADAPTER = configured_adapter_path()
EDITOR_READBACK_SECONDS = 60.0


async def _insert_text_once(session: object, query: str) -> None:
    """Use one CDP text-entry action, then let the pinned adapter read it back."""
    await session.send("Input.insertText", {"text": query})


def main(argv: list[str] | None = None) -> int:
    if not REFERENCE_ADAPTER.is_file():
        raise SystemExit("Read-only Scopus adapter is unavailable")
    spec = importlib.util.spec_from_file_location(
        "slr1_scopus_pilot003_read_only_adapter", REFERENCE_ADAPTER
    )
    if spec is None or spec.loader is None:
        raise SystemExit("Could not import the read-only Scopus adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.SCOPUS_NATIVE_EDITOR_ATTEMPT_TIMEOUT_SECONDS = EDITOR_READBACK_SECONDS
    # The pinned adapter still focuses/clears the visible Monaco field, then
    # verifies its exact EditContext text before its one native Search click.
    # Input.insertText is a target-scoped browser text-entry event, not a DOM
    # mutation or source/API shortcut; it prevents thousands of individual
    # key events from being lost while the current Monaco control hydrates.
    module._type_native_editor_query = _insert_text_once
    return module.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
