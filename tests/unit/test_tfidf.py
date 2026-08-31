import math

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.ranking.tfidf import TfIdfVectorizer


def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.add_document(1, ["python", "python", "python", "search"])
    index.add_document(2, ["python", "programming"])
    index.add_document(3, ["java", "programming"])
    return index


def test_idf_is_zero_for_term_in_every_document():
    index = InvertedIndex()
    index.add_document(1, ["common", "word"])
    index.add_document(2, ["common", "other"])
    vectorizer = TfIdfVectorizer(index)

    assert vectorizer.idf("common") == 0.0


def test_idf_is_higher_for_rarer_terms():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    assert vectorizer.idf("search") > vectorizer.idf("programming")


def test_idf_unseen_term_is_zero_not_error():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)
    assert vectorizer.idf("nonexistent") == 0.0


def test_tf_log_scaling_dampens_repeated_terms():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    tf_repeated = vectorizer.tf("python", doc_id=1)
    tf_single = vectorizer.tf("programming", doc_id=2)

    assert tf_single == 1.0
    assert tf_repeated == 1.0 + math.log10(3)
    assert tf_repeated < 3 * tf_single


def test_tf_unseen_term_in_doc_is_zero():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)
    assert vectorizer.tf("java", doc_id=1) == 0.0


def test_vectorize_document_only_includes_actual_terms():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    vector = vectorizer.vectorize_document(1)
    assert set(vector.keys()) == {"python", "search"}
    assert all(weight >= 0 for weight in vector.values())


def test_score_ranks_documents_sensibly():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    score_doc1 = vectorizer.score(["search"], doc_id=1)
    score_doc2 = vectorizer.score(["search"], doc_id=2)

    assert score_doc1 > 0
    assert score_doc2 == 0.0


def test_score_sums_multiple_query_terms():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    combined = vectorizer.score(["python", "search"], doc_id=1)
    individual_sum = vectorizer.tf_idf("python", 1) + vectorizer.tf_idf("search", 1)
    assert combined == individual_sum


def test_vectorize_query_counts_repeated_query_terms():
    index = _build_sample_index()
    vectorizer = TfIdfVectorizer(index)

    vector = vectorizer.vectorize_query(["python", "python", "search"])
    assert set(vector.keys()) == {"python", "search"}