import asyncio
import time

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.performance.async_search import (
    handle_many_queries_concurrently,
    handle_many_queries_sequentially,
    handle_query_async,
)
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.ranking.scorer import ResultScorer

def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.add_document(1, ["python", "search", "engine"])
    index.add_document(2, ["java", "programming"])
    index.add_document(3, ["python", "web", "framework"])
    return index

def test_single_async_query_returns_correct_results():
    index = _build_sample_index()
    scorer = ResultScorer(BM25Ranker(index))

    result = asyncio.run(
        handle_query_async(scorer, index, ["python"], top_k=5, simulated_io_latency=0.001)
    )
    doc_ids = {doc_id for doc_id, _ in result}
    assert doc_ids == {1, 3}

def test_concurrent_queries_produce_same_results_as_sequential():
    index = _build_sample_index()
    scorer = ResultScorer(BM25Ranker(index))
    queries = [["python"], ["java"], ["search", "engine"]]

    concurrent_results = asyncio.run(
        handle_many_queries_concurrently(scorer, index, queries, simulated_io_latency=0.001)
    )
    sequential_results = asyncio.run(
        handle_many_queries_sequentially(scorer, index, queries, simulated_io_latency=0.001)
    )

    assert concurrent_results == sequential_results

def test_concurrent_queries_are_meaningfully_faster_than_sequential():
    index = _build_sample_index()
    scorer = ResultScorer(BM25Ranker(index))
    queries = [["python"]] * 10
    io_latency = 0.02

    start = time.perf_counter()
    asyncio.run(handle_many_queries_concurrently(scorer, index, queries, simulated_io_latency=io_latency))
    concurrent_time = time.perf_counter() - start

    start = time.perf_counter()
    asyncio.run(handle_many_queries_sequentially(scorer, index, queries, simulated_io_latency=io_latency))
    sequential_time = time.perf_counter() - start

    assert concurrent_time < sequential_time / 2
    assert concurrent_time < io_latency * 3

def test_empty_query_list_returns_empty_results():
    index = _build_sample_index()
    scorer = ResultScorer(BM25Ranker(index))

    result = asyncio.run(handle_many_queries_concurrently(scorer, index, [], simulated_io_latency=0.001))
    assert result == []