import asyncio
import time

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.ranking.scorer import ResultScorer

async def handle_query_async(
    scorer: ResultScorer,
    index: InvertedIndex,
    query_terms: list[str],
    top_k: int = 10,
    simulated_io_latency: float = 0.01,
) -> list[tuple[int, float]]:
    await asyncio.sleep(simulated_io_latency)

    candidates: set[int] = set()
    for term in query_terms:
        candidates |= index.get_document_ids(term)

    return scorer.rank(query_terms, candidates, top_k=top_k)

async def handle_many_queries_concurrently(
    scorer: ResultScorer,
    index: InvertedIndex,
    queries: list[list[str]],
    top_k: int = 10,
    simulated_io_latency: float = 0.01,
) -> list[list[tuple[int, float]]]:

    tasks = [
        handle_query_async(scorer, index, query, top_k, simulated_io_latency)
        for query in queries
    ]
    return await asyncio.gather(*tasks)

async def handle_many_queries_sequentially(
    scorer: ResultScorer,
    index: InvertedIndex,
    queries: list[list[str]],
    top_k: int = 10,
    simulated_io_latency: float = 0.01,
) -> list[list[tuple[int, float]]]:
    results = []
    for query in queries:
        result = await handle_query_async(scorer, index, query, top_k, simulated_io_latency)
        results.append(result)
    return results