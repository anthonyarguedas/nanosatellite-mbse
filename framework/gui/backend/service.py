"""Source bootstrap for the GUI backend, including Python's -I mode."""

from pathlib import Path
import runpy
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    runpy.run_module("framework.gui.backend", run_name="__main__")
