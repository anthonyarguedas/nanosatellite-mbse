# SLR1 multimodal retrieval

The corpus contains structure aware text chunks, dedicated mathematical equation chunks, every source image, and GPT-5.6-Luna extractions of SysML, Capella/Arcadia, Simulink, and formal diagrams from the 140 included reports. It also includes all Markdown documents in `SLR/SLR1/pdfs/standards`, currently 25 sources. This collection includes standards, handbooks, guidance, previews, excerpts, and source access notes. Edition and availability metadata remain attached to results. Qwen3 provides text embeddings, ColPali searches the source images directly, and Qwen3-Reranker orders the fused candidates by default. Jev supports direct Noul scoring and API based reranking.

## Answer a question

```bash
cd embeddings
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode jev --top-k 12
```

Available modes, in descending order of observed performance:

- `jev`: **recommended**. sends each eligible chunk to Jev and ranks it by a query specific Noul probability. The query is part of the Noul instructions. This is direct semantic scoring, rather than an embedding or vector similarity search.
- `vector`: **recommended**. embeds the question with Qwen3, omits chunks below the cached Jev content threshold, finds semantic matches, and optionally reranks the shortlist.
- `visual`: matches the question directly against every report image with ColPali.
- `hybrid`: filters text chunks with the cached Jev content Noul, fuses Qwen3 vector, BM25, and available ColPali visual ranks, then reranks the top 50 candidates with Qwen3-Reranker. This is the default. If the visual index is missing, stale, or still building, the search continues with Qwen3 and BM25 and reports that it skipped visual retrieval.
- `bm25`: finds exact acronyms, tool names, numbers, and technical terms. Double-quoted terms receive an exact phrase bonus.
- `regex`: finds case insensitive Python regular expression matches in the original chunk text.

Use `--no-visual` for hybrid ablation runs. Every text mode supports Qwen or Jev reranking. Use `--no-rerank` to keep its first stage order. Change the candidate count with `--rerank-depth`. The final weighted rank fusion gives the reranker three times the weight of initial retrieval. Use `--images-only` to keep results linked to source images. Use `--reviews include` (the default), `--reviews exclude`, or `--reviews only` to control whether publication-type reviews appear. Use `--standards include` (the default), `--standards exclude`, or `--standards only` for the standards collection. The filters apply together. Restrict a standards search to one document with its filename code, such as `--report cds-14.1`.

```bash
echo "What electrical safety requirements apply to CubeSats?" \
  | .venv/bin/python search.py --mode vector --standards only
```

Set a TypeSafe API key to use direct Jev search or Jev reranking:

```bash
export TYPESAFE_API_KEY="..."
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode jev --top-k 12

# Jev can also rerank a Qwen shortlist.
echo "How is a CubeSat power budget verified?" \
  | .venv/bin/python search.py --mode vector --reranker jev
```

Direct Jev search uses up to 32 concurrent API requests and two Nouls. A fixed content Noul separates substantive report evidence from publication metadata, author and venue details, biographies, and reference lists. Chunks with a content Noul of at least `0.30` remain eligible. A query specific Noul scores relevance. The first search evaluates both questions for every chunk. Later searches skip chunks classified as metadata and send only substantive chunks that lack a cached score for that exact query. Repeating a query can run entirely from the cache.

The shared cache is `artifacts/jev-1.13.0/noul-index.sqlite3`. It records raw Noul probabilities, so policy thresholds can change without new API calls. Qwen Vector and Hybrid searches require complete content scores for the included reports and never call Jev themselves. New standards chunks remain searchable while their content scores are pending. Results report this incomplete coverage. Cached metadata classifications still apply, and unclassified chunks receive no fabricated Noul score. Run `build_jev_content_index.py` when API credits are available to classify only missing chunks, without scoring a search query. The file is configured for Git LFS. Add it with `git add artifacts/jev-1.13.0/noul-index.sqlite3` after a search. A direct search can make thousands of billable API requests when the cache is empty. Completed calls are committed as they return, so a failed or interrupted search resumes from its cached rows. Transient timeouts, connection failures, rate limits, and server errors are retried up to five times with no total retry budget. Each individual request retains a 120 second timeout. Search also reads the ignored `api-key.env` file in this directory when environment variables are absent.

For broad questions, split the question into focused subquestions. Retrieve 10 to 20 chunks for each.

## Use the browser interface

Run the local server from `embeddings`:

```bash
cd embeddings
.venv/bin/python search.py --serve --open
```

The GUI opens at `http://127.0.0.1:8765`.
It defaults to Vector search and also provides Hybrid, Jev Noul, BM25, and Regex methods. Choose Off, Qwen, or Jev reranking for any method. The Images only filter replaces the standalone Visual method in the GUI. The Reviews control can include reviews, exclude them, or return reviews only. The Standards control provides the same choices for the standards collection. The index status panel reports text, visual, and Jev cache coverage. Image results show the original file, its caption or Luna extraction when available, and a link to the source PDF.

Treat retrieved chunks as evidence candidates. Check important claims in the source Markdown.

Display equations receive dedicated `equation` chunks while remaining available in their original passage chunks. An adjacent sentence that explicitly names an equation becomes its caption. When no caption is present, the chunk includes preceding and following prose from the same section and nearby page. Equation ranges such as “Equations (1-4)” label consecutive formulas when the counts agree. Long formulas are split into numbered parts with repeated context.

## Rebuild after corpus changes

```bash
UV_CACHE_DIR=.cache/uv uv sync
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
.venv/bin/python build_visual_index.py --batch-size 1
# Requires TypeSafe credits. Reuses cached content scores.
.venv/bin/python build_jev_content_index.py
```

`prepare_corpus.py` discovers standards Markdown automatically. Adding standards does not change the authoritative included-report list. Preview, excerpt, historical, and access-note sources retain their original status. Consult the original source before using a requirement as authoritative.

`build_index.py` reuses vectors for chunks whose ID and embedding text are unchanged. Its tracked chunk-record sidecar allows reuse even when changed chunks are not a contiguous suffix.

To refresh visual diagram extraction first:

```bash
.venv/bin/python diagram_pipeline.py candidates
.venv/bin/python diagram_pipeline.py process --workers 8 --thinking minimal
.venv/bin/python prepare_corpus.py
.venv/bin/python build_index.py
.venv/bin/python build_visual_index.py --batch-size 1
```

`diagram_pipeline.py` selects images from caption and report evidence naming SysML, Capella, Arcadia, Simulink, formal automata, BIP, fault trees, Bayesian networks, GSN, fault propagation models, or formal state transition networks. It runs one `gpt-5.6-luna` subagent per candidate image. Use `process --stale-schema` to refresh results created with an older extraction schema, or `process --refresh` to replace every selected cached result. Accepted visual extractions are stored in `data/diagram-analyses.jsonl` and split into overview, element, relationship, relationship annotation, formal content, and visible label chunks.

`build_visual_index.py` independently discovers every image referenced by the included reports. It preserves the Luna metadata for accepted SysML, Capella/Arcadia, Simulink, and formal diagrams and indexes all images with `vidore/colpali-v1.3-hf`. The first build downloads the model and encodes the full image corpus. It caches each completed image, so an interrupted build resumes on the next run. Later builds reuse unchanged image vectors.

Add `--json` to `search.py` when passing results to another program.
