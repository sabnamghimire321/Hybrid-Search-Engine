import math

from search_engine.ranking.evaluation import ndcg_at_k, precision_at_k, recall_at_k

def test_precision_all_relevant():
    retrieved = [1, 2, 3]
    relevant = {1, 2, 3}
    assert precision_at_k(retrieved, relevant, k=3) == 1.0

def test_precision_none_relevant():
    retrieved = [1, 2, 3]
    relevant = {4, 5, 6}
    assert precision_at_k(retrieved, relevant, k=3) == 0.0

def test_precision_partial_match():
    retrieved = [1, 2, 3, 4]
    relevant = {1, 3}
    assert precision_at_k(retrieved, relevant, k=4) == 0.5

def test_precision_at_k_smaller_than_retrieved_list():
    retrieved = [1, 2, 3, 4, 5]
    relevant = {1, 2}
    assert precision_at_k(retrieved, relevant, k=2) == 1.0
    assert precision_at_k(retrieved, relevant, k=1) == 1.0

def test_precision_empty_retrieved_list():
    assert precision_at_k([], {1, 2}, k=5) == 0.0

def test_recall_finds_all_relevant():
    retrieved = [1, 2, 3]
    relevant = {1, 2}
    assert recall_at_k(retrieved, relevant, k=3) == 1.0

def test_recall_misses_some_relevant():
    retrieved = [1, 3]
    relevant = {1, 2, 3, 4}
    assert recall_at_k(retrieved, relevant, k=2) == 0.5

def test_recall_with_no_relevant_documents_at_all():
    assert recall_at_k([1, 2], set(), k=2) == 0.0

def test_recall_only_considers_top_k():
    retrieved = [5, 6, 1]
    relevant = {1}
    assert recall_at_k(retrieved, relevant, k=2) == 0.0
    assert recall_at_k(retrieved, relevant, k=3) == 1.0

def test_ndcg_perfect_ranking_scores_exactly_one():
    relevance_scores = {1: 3, 2: 2, 3: 1, 4: 0}
    perfect_order = [1, 2, 3, 4]
    assert math.isclose(ndcg_at_k(perfect_order, relevance_scores, k=4), 1.0)

def test_ndcg_worst_ranking_scores_less_than_one():
    relevance_scores = {1: 3, 2: 2, 3: 1, 4: 0}
    worst_order = [4, 3, 2, 1]
    score = ndcg_at_k(worst_order, relevance_scores, k=4)
    assert score < 1.0

def test_ndcg_classic_worked_example():
    relevance_scores = {1: 3, 2: 2, 3: 3, 4: 0, 5: 1, 6: 2}
    retrieved_order = [1, 2, 3, 4, 5, 6]

    result = ndcg_at_k(retrieved_order, relevance_scores, k=6)
    assert math.isclose(result, 0.9488107485678985, rel_tol=1e-9)

def test_ndcg_with_no_relevant_documents_returns_zero():
    assert ndcg_at_k([1, 2, 3], {}, k=3) == 0.0

def test_ndcg_missing_docs_treated_as_zero_relevance():
    relevance_scores = {1: 3}
    retrieved = [1, 999]
    result = ndcg_at_k(retrieved, relevance_scores, k=2)
    assert 0.0 < result <= 1.0