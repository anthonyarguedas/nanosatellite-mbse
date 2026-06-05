#!/usr/bin/env python3
"""Run the full SLR1 KG + embedding experiment pipeline (scripts 01--09)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE = [
    "01_flatten_extraction.py",
    "02_build_kg.py",
    "03_controlled_graph_analyses.py",
    "04_build_embedding_cards.py",
    "05_embed_and_neighbors.py",
    "06_semantic_analyses.py",
    "07_hybrid_graph.py",
    "08_graphrag_demo.py",
    "09_research_agenda.py",
]


def main() -> int:
    repo_root = SCRIPT_DIR.parents[3]
    print("SLR1 KG + embedding experiment pipeline")
    print(f"Repository root: {repo_root}")
    for index, script_name in enumerate(PIPELINE, start=1):
        script_path = SCRIPT_DIR / script_name
        if not script_path.exists():
            print(f"[{index:02d}/{len(PIPELINE):02d}] MISSING {script_name}", file=sys.stderr)
            return 1
        print(f"\n[{index:02d}/{len(PIPELINE):02d}] Running {script_name} ...", flush=True)
        completed = subprocess.run([sys.executable, str(script_path)], cwd=repo_root)
        if completed.returncode != 0:
            print(f"[{index:02d}/{len(PIPELINE):02d}] FAILED {script_name} (exit {completed.returncode})", file=sys.stderr)
            return completed.returncode or 1
        print(f"[{index:02d}/{len(PIPELINE):02d}] Completed {script_name}", flush=True)
    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
