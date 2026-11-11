"""Trusted source-checkout bootstrap for python -I -B -u service.py.

Installed deployments can use python -I -m nanosat_mbse.service instead.
"""

from pathlib import Path
import runpy
import sys

source = Path(__file__).resolve().parent / "src"
if not (source / "nanosat_mbse" / "service" / "__main__.py").is_file():
    raise SystemExit(
        "The nanosat_mbse source service is unavailable. Install the package and use -m nanosat_mbse.service."
    )
sys.path.insert(0, str(source))
runpy.run_module("nanosat_mbse.service", run_name="__main__")
