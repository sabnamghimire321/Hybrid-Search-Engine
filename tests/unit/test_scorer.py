import math

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.bm25 import BM25Ranker
from search_engine.ranking.scorer import ResultScorer


def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.add_document(1, ["python", "search", "engine"])
    index.add_document(2, ["python", "python", "python", "tutorial"])
    index.add_document(3, ["java", "programming"])
    return index


def test_rank_orders_by_score_descending():
    index = _build_sample_index()
    ranker = BM25Ranker(index)
    scorer = ResultScorer(ranker)

    results = scorer.rank(["python"], candidate_doc_ids=[1, 2, 3])
    doc_ids_in_order = [doc_id for doc_id, _ in results]

    assert doc_ids_in_order[0] == 2
    assert doc_ids_in_order[-1] == 3
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)


def test_rank_respects_top_k():
    index = _build_sample_index()
    ranker = BM25Ranker(index)
    scorer = ResultScorer(ranker)

    results = scorer.rank(["python"], candidate_doc_ids=[1, 2, 3], top_k=2)
    assert len(results) == 2
    doc_ids = {doc_id for doc_id, _ in results}
    assert doc_ids == {1, 2}


def test_top_k_matches_full_sort_truncated():
    index = _build_sample_index()
    ranker = BM25Ranker(index)
    scorer = ResultScorer(ranker)

    full = scorer.rank(["python"], candidate_doc_ids=[1, 2, 3])
    top2 = scorer.rank(["python"], candidate_doc_ids=[1, 2, 3], top_k=2)

    assert top2 == full[:2]


def test_pagerank_blending_changes_ranking():
    index = InvertedIndex()
    index.add_document(1, ["python", "search"])
    index.add_document(2, ["python", "search"])

    ranker = BM25Ranker(index)
    pagerank_scores = {1: 0.1, 2: 0.9}

    scorer = ResultScorer(ranker, pagerank_scores=pagerank_scores, pagerank_weight=10.0)
    results = scorer.rank(["python"], candidate_doc_ids=[1, 2])

    assert results[0][0] == 2


def test_pagerank_weight_zero_ignores_pagerank_by_default():
    index = InvertedIndex()
    index.add_document(1, ["python", "search"])
    index.add_document(2, ["python", "search"])

    ranker = BM25Ranker(index)
    pagerank_scores = {1: 0.1, 2: 0.9}
    scorer = ResultScorer(ranker, pagerank_scores=pagerank_scores)

    score1 = scorer.score_document(["python"], 1)
    score2 = scorer.score_document(["python"], 2)
    assert math.isclose(score1, score2)


def test_empty_candidates_returns_empty_list():
    index = _build_sample_index()
    ranker = BM25Ranker(index)
    scorer = ResultScorer(ranker)

    assert scorer.rank(["python"], candidate_doc_ids=[]) == []