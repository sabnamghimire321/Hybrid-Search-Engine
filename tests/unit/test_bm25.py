from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.bm25 import BM25Ranker

def test_idf_never_negative_even_for_universal_term():
    index = InvertedIndex()
    index.add_document(1, ["common", "word"])
    index.add_document(2, ["common", "other"])
    index.add_document(3, ["common", "thing"])

    ranker = BM25Ranker(index)
    assert ranker.idf("common") >= 0.0

def test_term_frequency_saturation_is_sublinear():
    index = InvertedIndex()
    tokens_a = ["target"] + [f"filler_a{i}" for i in range(19)]
    tokens_b = ["target"] * 10 + [f"filler_b{i}" for i in range(10)]
    index.add_document(1, tokens_a)
    index.add_document(2, tokens_b)

    ranker = BM25Ranker(index)
    score_tf1 = ranker.score(["target"], doc_id=1)
    score_tf10 = ranker.score(["target"], doc_id=2)

    assert score_tf10 > score_tf1
    assert score_tf10 < 10 * score_tf1

def test_shorter_document_scores_higher_for_equal_term_frequency():
    index = InvertedIndex()
    tokens_short = ["target"] + [f"filler_a{i}" for i in range(9)]
    tokens_long = ["target"] + [f"filler_b{i}" for i in range(99)]
    index.add_document(1, tokens_short)
    index.add_document(2, tokens_long)

    ranker = BM25Ranker(index)
    score_short = ranker.score(["target"], doc_id=1)
    score_long = ranker.score(["target"], doc_id=2)

    assert score_short > score_long

def test_b_zero_disables_length_normalization():
    index = InvertedIndex()
    tokens_short = ["target"] + [f"filler_a{i}" for i in range(9)]
    tokens_long = ["target"] + [f"filler_b{i}" for i in range(99)]
    index.add_document(1, tokens_short)
    index.add_document(2, tokens_long)

    ranker = BM25Ranker(index, b=0.0)
    score_short = ranker.score(["target"], doc_id=1)
    score_long = ranker.score(["target"], doc_id=2)

    assert score_short == score_long

def test_k1_zero_makes_term_frequency_irrelevant():
    index = InvertedIndex()
    tokens_rare = ["target"] + [f"filler_a{i}" for i in range(19)]
    tokens_frequent = ["target"] * 15 + [f"filler_b{i}" for i in range(5)]
    index.add_document(1, tokens_rare)
    index.add_document(2, tokens_frequent)

    ranker = BM25Ranker(index, k1=0.0)
    score_rare = ranker.score(["target"], doc_id=1)
    score_frequent = ranker.score(["target"], doc_id=2)

    assert score_rare == score_frequent == ranker.idf("target")

def test_absent_query_term_contributes_zero():
    index = InvertedIndex()
    index.add_document(1, ["python", "search"])
    index.add_document(2, ["java", "programming"])

    ranker = BM25Ranker(index)
    assert ranker.score(["nonexistent"], doc_id=1) == 0.0

def test_empty_index_does_not_crash():
    index = InvertedIndex()
    ranker = BM25Ranker(index)
    assert ranker.score(["anything"], doc_id=1) == 0.0

def test_multi_term_query_sums_contributions():
    index = InvertedIndex()
    index.add_document(1, ["python", "search", "engine"])
    index.add_document(2, ["java", "programming"])

    ranker = BM25Ranker(index)
    combined = ranker.score(["python", "search"], doc_id=1)
    individual_sum = ranker.score(["python"], doc_id=1) + ranker.score(["search"], doc_id=1)
    assert combined == individual_sum