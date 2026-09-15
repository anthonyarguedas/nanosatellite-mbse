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

For broad questions, split the question into focused subquestions. Retrieve 10 to 20 chunks for each. Give those chunks to an LLM with this instruction:

> Answer only from the supplied excerpts. Cite `report_id` and page for every claim. Separate observed results from author claims and future work. State when evidence is insufficient or conflicting.

Treat retrieved chunks as evidence candidates. Check important claims in the source Markdown.

## Explore themes with clustering

Cluster report-level centroids so long theses do not dominate:

```bash
.venv/bin/python cluster.py --level report --clusters 12
```

For finer themes:

```bash
.venv/bin/python cluster.py --level chunk --clusters 30
```

Read the representative items in `artifacts/qwen3-embedding-0.6b/clusters-*.json` and assign human theme labels. Clusters support exploration and sampling. They do not establish findings or frequencies.

## Rebuild after corpus changes

```bash
UV_CACHE_DIR=.cache/uv uv sync
./convert_missing_sources.sh
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
```

Add `--json` to `search.py` when passing results to another program.
