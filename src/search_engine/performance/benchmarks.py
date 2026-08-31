import random
import statistics
import time

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.ranking.scorer import ResultScorer

_VOCAB = [f"word{i}" for i in range(500)]

def generate_synthetic_corpus(
    num_docs: int, doc_length: int = 100, seed: int = 42
) -> dict[int, list[str]]:
    rng = random.Random(seed)
    return {
        doc_id: [rng.choice(_VOCAB) for _ in range(doc_length)] for doc_id in range(num_docs)
    }

def benchmark_indexing(num_docs: int, doc_length: int = 100) -> dict:
    corpus = generate_synthetic_corpus(num_docs, doc_length)

    start = time.perf_counter()
    index = InvertedIndex()
    for doc_id, tokens in corpus.items():
        index.add_document(doc_id, tokens)
    elapsed = time.perf_counter() - start

    return {
        "num_docs": num_docs,
        "doc_length": doc_length,
        "total_seconds": elapsed,
        "docs_per_second": num_docs / elapsed if elapsed > 0 else float("inf"),
    }

def benchmark_search_latency(index: InvertedIndex, num_queries: int = 200, seed: int = 7) -> dict:
    rng = random.Random(seed)
    ranker = BM25Ranker(index)
    scorer = ResultScorer(ranker)

    latencies_ms = []
    for _ in range(num_queries):
        query_terms = [rng.choice(_VOCAB) for _ in range(rng.randint(1, 3))]

        start = time.perf_counter()
        candidates: set[int] = set()
        for term in query_terms:
            candidates |= index.get_document_ids(term)
        scorer.rank(query_terms, candidates, top_k=10)
        latencies_ms.append((time.perf_counter() - start) * 1000)

    latencies_ms.sort()
    n = len(latencies_ms)

    return {
        "num_queries": num_queries,
        "corpus_size": index.document_count,
        "mean_ms": statistics.mean(latencies_ms),
        "p50_ms": latencies_ms[n // 2],
        "p95_ms": latencies_ms[int(n * 0.95)],
        "p99_ms": latencies_ms[min(int(n * 0.99), n - 1)],
        "max_ms": latencies_ms[-1],
    }

def run_full_benchmark_report(num_docs: int = 5000, num_queries: int = 200) -> None:
    print(f"Building synthetic corpus of {num_docs} documents...")
    index_stats = benchmark_indexing(num_docs)
    print(
        f"  Indexed {index_stats['num_docs']} docs in "
        f"{index_stats['total_seconds']:.3f}s "
        f"({index_stats['docs_per_second']:.0f} docs/sec)"
    )

    corpus = generate_synthetic_corpus(num_docs)
    index = InvertedIndex()
    for doc_id, tokens in corpus.items():
        index.add_document(doc_id, tokens)

    print(f"\nRunning {num_queries} search queries...")
    search_stats = benchmark_search_latency(index, num_queries)
    print(f"  Mean latency: {search_stats['mean_ms']:.3f} ms")
    print(f"  p50 latency:  {search_stats['p50_ms']:.3f} ms")
    print(f"  p95 latency:  {search_stats['p95_ms']:.3f} ms")
    print(f"  p99 latency:  {search_stats['p99_ms']:.3f} ms")
    print(f"  Max latency:  {search_stats['max_ms']:.3f} ms")


if __name__ == "__main__":
    run_full_benchmark_report()