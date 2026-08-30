"""Portable Scopus adapter configuration for Pilot 003."""

from __future__ import annotations

import os
from pathlib import Path


ADAPTER_ENVIRONMENT_VARIABLE = "SCOPUS_ADAPTER"
DEFAULT_ADAPTER_REFERENCE = (
    "$HOME/agent-tools/internet/skills/browser/scripts/search_scopus.py"
)
FOCUSED_ADAPTER_REFERENCE = "scripts/scopus_pilot003/focused_adapter.py"


def configured_adapter_path() -> Path:
    """Return the configured read-only adapter path for execution."""
    setting = os.environ.get(ADAPTER_ENVIRONMENT_VARIABLE) or DEFAULT_ADAPTER_REFERENCE
    return Path(os.path.expandvars(setting)).expanduser()


def configured_adapter_reference() -> str:
    """Return a portable adapter reference for locally written receipts."""
    if os.environ.get(ADAPTER_ENVIRONMENT_VARIABLE):
        return f"${ADAPTER_ENVIRONMENT_VARIABLE}"
    return DEFAULT_ADAPTER_REFERENCE
