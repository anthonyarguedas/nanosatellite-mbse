# SLR1 Qwen retrieval

The corpus contains text chunks and visually extracted SysML and Capella/Arcadia diagram chunks from the 133 included reports. Metadata in `data/chunks.jsonl` preserves the report, title, section, page, chunk type, source text, and source image. Qwen vectors are in `artifacts/qwen3-embedding-0.6b/`.

## Answer a question

Use hybrid retrieval by default:

```bash
cd embeddings
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode hybrid --top-k 12
```

Available modes:

- `dense`: embeds the question with Qwen and finds semantic matches.
- `bm25`: finds exact acronyms, tool names, numbers, and technical terms. Double-quoted terms receive an exact phrase bonus.
- `hybrid`: combines dense and BM25 ranks. This is usually the safest choice.

For broad questions, split the question into focused subquestions. Retrieve 10 to 20 chunks for each.

Treat retrieved chunks as evidence candidates. Check important claims in the source Markdown.

## Rebuild after corpus changes

```bash
UV_CACHE_DIR=.cache/uv uv sync
./convert_missing_sources.sh
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
```

To refresh visual diagram extraction first:

```bash
.venv/bin/python diagram_pipeline.py candidates
.venv/bin/python diagram_pipeline.py process --workers 8 --thinking minimal
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
```

`diagram_pipeline.py` selects images from caption chunks that name SysML, Capella, Arcadia, a native diagram type, or a model representation term. It also includes uncaptioned images when the report title names SysML, Capella, or Arcadia. It runs one `gpt-5.6-luna` subagent per candidate image. Accepted visual extractions are stored in `data/diagram-analyses.jsonl` and split into overview, element, relationship, and visible label chunks.

Add `--json` to `search.py` when passing results to another program.
