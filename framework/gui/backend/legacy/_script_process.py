"""Private subprocess adapter for trusted, importable analysis classes."""

from __future__ import annotations

import importlib
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

# -I ignores PYTHONPATH. Insert only the installed/source package's own root.
# Invocation metadata is built by IsolatedRunner, never supplied by the browser.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from framework.gui.backend.legacy.verification import VerificationScript


def main():
    try:
        request = json.load(sys.stdin)
        cls = importlib.import_module(request["classModule"])
        for name in request["className"].split("."):
            cls = getattr(cls, name)
        if not isinstance(cls, type) or not issubclass(cls, VerificationScript):
            raise TypeError(
                "The selected implementation must inherit VerificationScript."
            )
        script = cls()
        if (
            script.definition != request["definition"]
            or script.current_revision != request["implementationRevision"]
        ):
            raise ValueError(
                "The analysis implementation changed before execution. Reload and review its definition."
            )
        inputs = script.validate_inputs(request["inputs"])
        with redirect_stdout(sys.stderr):
            values = script.calculate(
                inputs,
                requirements=request.get("requirements", {}),
                mode=request.get("mode"),
            )
        json.dump(script.validate_outputs(values), sys.stdout, allow_nan=False)
        return 0
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
