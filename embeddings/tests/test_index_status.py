from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from index_status import file_sha256, inspect_indexes


class IndexStatusTests(unittest.TestCase):
    def write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")

    def fixture(self, root: Path, create_figure: bool = True) -> dict:
        data = root / "data"
        text_artifacts = root / "artifacts/text"
        visual_artifacts = root / "artifacts/visual"
        report_dir = root / "reports/report-0001"
        report_dir.mkdir(parents=True)
        source = report_dir / "report-0001.md"
        source.write_text(
            "<!-- PDF_PAGE: 1 -->\n![figure_001.png](figure_001.png)\n",
            encoding="utf-8",
        )
        figure = report_dir / "figure_001.png"
        if create_figure:
            figure.write_bytes(b"figure one")
        reports_path = data / "reports.jsonl"
        self.write_jsonl(
            reports_path,
            [
                {
                    "report_id": "review-0001",
                    "title": "Example",
                    "source_path": "reports/report-0001/report-0001.md",
                }
            ],
        )
        chunks_path = data / "chunks.jsonl"
        self.write_jsonl(chunks_path, [{"chunk_id": "one"}, {"chunk_id": "two"}])
        self.write_jsonl(data / "units.jsonl", [])
        self.write_jsonl(data / "diagram-analyses.jsonl", [])

        text_artifacts.mkdir(parents=True)
        np.save(
            text_artifacts / "document-embeddings.f32.npy",
            np.zeros((2, 4), dtype=np.float32),
        )
        (text_artifacts / "index-manifest.json").write_text(
            json.dumps(
                {
                    "model_id": "text-model",
                    "model_revision": "text-revision",
                    "chunks_sha256": file_sha256(chunks_path),
                    "chunks": 2,
                }
            ),
            encoding="utf-8",
        )
        return {
            "repository_root": root,
            "data_dir": data,
            "text_artifact_dir": text_artifacts,
            "text_model_id": "text-model",
            "text_model_revision": "text-revision",
            "images_path": data / "images.jsonl",
            "visual_vectors_path": visual_artifacts / "vectors.npy",
            "visual_manifest_path": visual_artifacts / "index-manifest.json",
            "visual_cache_dir": visual_artifacts / ".build-cache",
            "visual_build_state_path": visual_artifacts / "build-state.json",
            "visual_model_id": "visual-model",
            "visual_model_revision": "visual-revision",
            "figure": figure,
        }

    def inspect(self, paths: dict) -> dict:
        options = {key: value for key, value in paths.items() if key != "figure"}
        return inspect_indexes(**options)

    def test_reports_ready_text_and_missing_visual_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.fixture(Path(temporary), create_figure=False)

            status = self.inspect(paths)

        self.assertEqual(status["text"]["state"], "ready")
        self.assertEqual(status["visual"]["state"], "missing")
        self.assertEqual(status["corpus"]["figures"], 1)
        self.assertEqual(status["corpus"]["missing_figures"], 1)
        self.assertEqual(status["visual"]["unindexed_figures"], 1)

    def test_changed_figure_marks_visual_index_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self.fixture(Path(temporary))
            data = paths["data_dir"]
            visual_artifacts = paths["visual_manifest_path"].parent
            visual_artifacts.mkdir(parents=True)
            source_image = "reports/report-0001/figure_001.png"
            record = {
                "image_id": "review-0001--image-figure-001",
                "report_id": "review-0001",
                "title": "Example",
                "source_image": source_image,
                "source_image_sha256": file_sha256(paths["figure"]),
            }
            self.write_jsonl(paths["images_path"], [record])
            np.save(
                paths["visual_vectors_path"],
                np.zeros((1, 3, 4), dtype=np.float16),
            )
            paths["visual_manifest_path"].write_text(
                json.dumps(
                    {
                        "model_id": "visual-model",
                        "model_revision": "visual-revision",
                        "images_sha256": file_sha256(paths["images_path"]),
                        "reports_sha256": file_sha256(data / "reports.jsonl"),
                        "units_sha256": file_sha256(data / "units.jsonl"),
                        "diagram_analyses_sha256": file_sha256(
                            data / "diagram-analyses.jsonl"
                        ),
                        "images": 1,
                    }
                ),
                encoding="utf-8",
            )

            ready = self.inspect(paths)
            paths["figure"].write_bytes(b"changed figure")
            stale = self.inspect(paths)

        self.assertEqual(ready["visual"]["state"], "ready")
        self.assertEqual(stale["visual"]["state"], "stale")
        self.assertEqual(stale["visual"]["changed_figures"], 1)


if __name__ == "__main__":
    unittest.main()
