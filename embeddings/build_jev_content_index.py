#!/usr/bin/env python3
"""Cache missing Jev content classifications without scoring a search query."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from search import (
    DATA_DIR,
    JEV_CONTENT_QUESTION,
    JEV_CONTENT_QUESTION_ID,
    JEV_MODEL_ID,
    JEV_SEARCH_WORKERS,
    JevSearchIndex,
    SearchError,
    SearchService,
    file_sha256,
    jev_chunk_state,
    json_sha256,
    read_jsonl,
    response_noul,
)


def build(service: SearchService, workers: int = JEV_SEARCH_WORKERS) -> dict:
    """Reuse all valid scores and commit each new classification as it returns."""
    if workers < 1:
        raise ValueError("The worker count must be at least 1.")
    chunks_path = DATA_DIR / "chunks.jsonl"
    corpus_sha256 = file_sha256(chunks_path)
    chunks = read_jsonl(chunks_path)
    if file_sha256(chunks_path) != corpus_sha256:
        raise RuntimeError("Chunk corpus changed while it was being read")
    states = [jev_chunk_state(chunk) for chunk in chunks]
    chunk_states = [
        (str(chunk["chunk_id"]), json_sha256(state))
        for chunk, state in zip(chunks, states)
    ]
    with JevSearchIndex(service.jev_index_path) as index:
        index.sync_corpus(chunk_states, corpus_sha256)
        cached = index.content_scores()
        tasks = [
            row
            for row, (chunk_id, _) in enumerate(chunk_states)
            if chunk_id not in cached
        ]
        print(
            f"Reused {len(cached)} content scores. Classifying {len(tasks)} chunks.",
            flush=True,
        )
        api_calls = 0
        if tasks:
            client = service._get_jev_client()

            def evaluate(row: int) -> float:
                response = client.system_one(
                    state=states[row],
                    questions={JEV_CONTENT_QUESTION_ID: JEV_CONTENT_QUESTION},
                    model=JEV_MODEL_ID,
                )
                return response_noul(response, JEV_CONTENT_QUESTION_ID)

            task_iterator = iter(tasks)
            failure: Exception | None = None
            with ThreadPoolExecutor(max_workers=min(workers, len(tasks))) as pool:
                pending = {}

                def submit_next() -> None:
                    row = next(task_iterator, None)
                    if row is not None:
                        pending[pool.submit(evaluate, row)] = row

                for _ in range(min(workers, len(tasks))):
                    submit_next()
                while pending:
                    completed, _ = wait(pending, return_when=FIRST_COMPLETED)
                    for future in completed:
                        row = pending.pop(future)
                        if future.cancelled():
                            continue
                        try:
                            noul = future.result()
                        except Exception as error:
                            failure = error
                            continue
                        chunk_id, state_sha256 = chunk_states[row]
                        index.save_evaluation(
                            search_id="",
                            chunk_id=chunk_id,
                            state_sha256=state_sha256,
                            query_noul=None,
                            content_noul=noul,
                        )
                        api_calls += 1
                        if api_calls % 100 == 0 or api_calls == len(tasks):
                            print(
                                f"[{api_calls}/{len(tasks)}] content scores cached",
                                flush=True,
                            )
                        if failure is None:
                            submit_next()
                    if failure is not None:
                        for future in pending:
                            future.cancel()
            if failure is not None:
                raise SearchError(
                    f"Jev content indexing stopped after caching {api_calls} new scores: {failure}"
                ) from failure
    if file_sha256(chunks_path) != corpus_sha256:
        raise RuntimeError(
            "Chunk corpus changed during content indexing. Run the build again."
        )
    return {"chunks": len(chunks), "reused_chunks": len(cached), "api_calls": api_calls}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=JEV_SEARCH_WORKERS)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("The worker count must be at least 1")
    try:
        result = build(SearchService(), args.workers)
    except (OSError, RuntimeError, SearchError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
