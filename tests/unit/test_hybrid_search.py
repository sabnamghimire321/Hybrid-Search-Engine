from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.semantic.embeddings import HashEmbeddingProvider
from search_engine.semantic.hybrid_search import HybridSearch

def _build_setup():
    index = InvertedIndex()
    index.add_document(1, ["python", "programming", "tutorial"])
    index.add_document(2, ["java", "programming", "guide"])
    index.add_document(3, ["python", "python", "python", "advanced"])
    bm25 = BM25Ranker(index)

    provider = HashEmbeddingProvider(dimension=32)
    doc_vectors = {
        1: provider.embed("python programming tutorial"),
        2: provider.embed("java programming guide"),
        3: provider.embed("python python python advanced"),
    }
    return bm25, provider, doc_vectors

def test_pure_keyword_search_matches_bm25_ranking():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=1.0)

    results = hybrid.search(
        query="python programming",
        query_terms=["python", "programming"],
        candidate_doc_ids=[1, 2, 3],
    )
    doc_ids_in_order = [doc_id for doc_id, _ in results]

    assert doc_ids_in_order[0] in (1, 3)
    assert doc_ids_in_order[-1] == 2

def test_pure_semantic_search_uses_only_embeddings():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=0.0)

    results = hybrid.search(
        query="python programming",
        query_terms=["python", "programming"],
        candidate_doc_ids=[1, 2, 3],
    )
    assert len(results) == 3

def test_scores_are_normalized_to_zero_one_range():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=0.5)

    results = hybrid.search(
        query="python programming",
        query_terms=["python", "programming"],
        candidate_doc_ids=[1, 2, 3],
    )
    for _, score in results:
        assert 0.0 <= score <= 1.0

def test_results_sorted_descending_by_combined_score():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=0.5)

    results = hybrid.search(
        query="python programming",
        query_terms=["python", "programming"],
        candidate_doc_ids=[1, 2, 3],
    )
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)

def test_top_k_limits_results():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=0.5)

    results = hybrid.search(
        query="python", query_terms=["python"], candidate_doc_ids=[1, 2, 3], top_k=2
    )
    assert len(results) == 2

def test_empty_candidates_returns_empty_list():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors)

    results = hybrid.search(query="python", query_terms=["python"], candidate_doc_ids=[])
    assert results == []

def test_all_identical_scores_do_not_crash_normalization():
    bm25, provider, doc_vectors = _build_setup()
    hybrid = HybridSearch(bm25, provider, doc_vectors, keyword_weight=0.5)

    results = hybrid.search(
        query="python", query_terms=["python"], candidate_doc_ids=[1]
    )
    assert len(results) == 1
    assert 0.0 <= results[0][1] <= 1.0