# SLR1 multimodal retrieval

The corpus contains structure aware text chunks, dedicated mathematical equation chunks, every source image, and GPT-5.6-Luna extractions of SysML, Capella/Arcadia, and Simulink diagrams from the 129 included reports. Qwen3 provides text embeddings, ColPali searches the source images directly, and Qwen3-Reranker orders the fused candidates.

## Answer a question

Use hybrid retrieval by default:

```bash
cd embeddings
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode hybrid --top-k 12
```

Available modes:

- `hybrid`: fuses Qwen3 vector, BM25, and available ColPali visual ranks, then reranks the top 50 candidates with Qwen3-Reranker. This is the default. If the visual index is missing, stale, or still building, the search continues with Qwen3 and BM25 and reports that it skipped visual retrieval.
- `vector`: embeds the question with Qwen3 and finds semantic text matches. `dense` remains an alias.
- `visual`: matches the question directly against every report image with ColPali.
- `bm25`: finds exact acronyms, tool names, numbers, and technical terms. Double-quoted terms receive an exact phrase bonus.
- `regex`: finds case insensitive Python regular expression matches in the original chunk text.

Use `--no-visual` or `--no-rerank` for hybrid ablation runs. Change the candidate count with `--rerank-depth`.

For broad questions, split the question into focused subquestions. Retrieve 10 to 20 chunks for each.

## Use the browser interface

Run the local server from `embeddings`:

```bash
cd embeddings
.venv/bin/python search.py --serve --open
```

The GUI opens at `http://127.0.0.1:8765`.
It provides Hybrid, Vector, Visual, BM25, and Regex modes and a result count slider. The index status panel reports text and visual index freshness, resumable build progress, unindexed figures, changed figures, and missing source files. Image results show the original file, its caption or Luna extraction when available, and a link to the source PDF.

Treat retrieved chunks as evidence candidates. Check important claims in the source Markdown.

Display equations receive dedicated `equation` chunks while remaining available in their original passage chunks. An adjacent sentence that explicitly names an equation becomes its caption. When no caption is present, the chunk includes preceding and following prose from the same section and nearby page. Equation ranges such as “Equations (1-4)” label consecutive formulas when the counts agree. Long formulas are split into numbered parts with repeated context.

## Rebuild after corpus changes

```bash
UV_CACHE_DIR=.cache/uv uv sync
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
.venv/bin/python build_visual_index.py --batch-size 1
```

To refresh visual diagram extraction first:

```bash
.venv/bin/python diagram_pipeline.py candidates
.venv/bin/python diagram_pipeline.py process --workers 8 --thinking minimal
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
.venv/bin/python build_visual_index.py --batch-size 1
```

`diagram_pipeline.py` selects images from caption chunks that name SysML, Capella, Arcadia, Simulink, a native diagram type, or a model representation term. It also selects captioned images from sections that discuss Simulink, which catches figures whose short captions omit the tool name. Uncaptioned images are included when the report title names one of these modeling languages or tools. It runs one `gpt-5.6-luna` subagent per candidate image. Accepted visual extractions are stored in `data/diagram-analyses.jsonl` and split into overview, element, relationship, and visible label chunks.

`build_visual_index.py` independently discovers every image referenced by the included reports. It preserves the Luna metadata for accepted SysML, Capella/Arcadia, and Simulink diagrams and indexes all images with `vidore/colpali-v1.3-hf`. The first build downloads the model and encodes the full image corpus. It caches each completed image, so an interrupted build resumes on the next run. Later builds reuse unchanged image vectors.

Add `--json` to `search.py` when passing results to another program.
