# SLR1 Qwen retrieval

The corpus contains 14,726 chunks from the 133 included reports. Metadata in `data/chunks.jsonl` preserves the report, title, section, page, chunk type, and source text. Qwen vectors are in `artifacts/qwen3-embedding-0.6b/`.

## Answer a question

Use hybrid retrieval by default:

```bash
cd embeddings
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode hybrid --top-k 12
```

Available modes:

- `dense`: embeds the question with Qwen and finds semantic matches.
- `bm25`: finds exact acronyms, tool names, numbers, and technical terms.
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

Add `--json` to `search.py` when passing results to another program.
