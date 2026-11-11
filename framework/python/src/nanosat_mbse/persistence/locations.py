"""Shared storage locations for the UI service and native command-line tools."""

from __future__ import annotations

import os
from pathlib import Path


def default_workspace() -> Path:
    """Select the current session without depending on existing session data."""
    configured = os.environ.get("MISSION_FILE")
    if configured:
        return Path(configured).expanduser().absolute()
    candidates = (*Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents)
    for parent in candidates:
        for framework in (parent, parent / "framework"):
            if (framework / "requirements-ui").is_dir() and (
                framework / "python"
            ).is_dir():
                return framework / "sessions" / "current.py"
    return Path.cwd() / "sessions" / "current.py"


def named_sessions_directory(model_path) -> Path:
    """Reuse a sessions directory, or select one beside a custom workspace."""
    parent = Path(model_path).expanduser().absolute().parent
    return parent if parent.name == "sessions" else parent / "sessions"
