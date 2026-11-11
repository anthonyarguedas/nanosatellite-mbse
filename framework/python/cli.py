"""Trusted source-checkout bootstrap for native command-line tools."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nanosat_mbse.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
