from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.performance.benchmarks import (
    benchmark_indexing,
    benchmark_search_latency,
    generate_synthetic_corpus,
)

def test_generate_synthetic_corpus_produces_requested_doc_count():
    corpus = generate_synthetic_corpus(num_docs=50, doc_length=20)
    assert len(corpus) == 50
    assert all(len(tokens) == 20 for tokens in corpus.values())

def test_generate_synthetic_corpus_is_deterministic_with_same_seed():
    corpus_a = generate_synthetic_corpus(num_docs=10, doc_length=5, seed=99)
    corpus_b = generate_synthetic_corpus(num_docs=10, doc_length=5, seed=99)
    assert corpus_a == corpus_b

def test_different_seeds_produce_different_corpora():
    corpus_a = generate_synthetic_corpus(num_docs=10, doc_length=20, seed=1)
    corpus_b = generate_synthetic_corpus(num_docs=10, doc_length=20, seed=2)
    assert corpus_a != corpus_b

def test_benchmark_indexing_returns_expected_fields():
    stats = benchmark_indexing(num_docs=100, doc_length=10)
    assert stats["num_docs"] == 100
    assert stats["total_seconds"] > 0
    assert stats["docs_per_second"] > 0

def test_benchmark_search_latency_returns_expected_fields():
    index = InvertedIndex()
    corpus = generate_synthetic_corpus(num_docs=100, doc_length=20)
    for doc_id, tokens in corpus.items():
        index.add_document(doc_id, tokens)

    stats = benchmark_search_latency(index, num_queries=20)

    assert stats["num_queries"] == 20
    assert stats["corpus_size"] == 100
    assert stats["p50_ms"] <= stats["p95_ms"] <= stats["p99_ms"] <= stats["max_ms"]
    assert stats["mean_ms"] >= 0

def test_benchmark_search_latency_on_empty_index_does_not_crash():
    index = InvertedIndex()
    stats = benchmark_search_latency(index, num_queries=5)
    assert stats["corpus_size"] == 0