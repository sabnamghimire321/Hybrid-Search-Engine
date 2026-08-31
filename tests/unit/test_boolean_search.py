from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.core.query.boolean_search import BooleanSearch


def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    pipeline = Pipeline()
    docs = {
        1: "python is a great programming language",
        2: "python is used for web development",
        3: "java is a programming language too",
        4: "rust is a systems programming language",
    }
    for doc_id, text in docs.items():
        index.add_document(doc_id, pipeline.process(text))
    return index


def test_search_and_intersection():
    search = BooleanSearch(_build_sample_index())
    assert search.search_and(["python", "programming"]) == {1}


def test_search_or_union():
    search = BooleanSearch(_build_sample_index())
    assert search.search_or(["python", "java"]) == {1, 2, 3}


def test_search_not_complement():
    search = BooleanSearch(_build_sample_index())
    assert search.search_not("python") == {3, 4}


def test_search_and_with_no_overlap_returns_empty():
    search = BooleanSearch(_build_sample_index())
    assert search.search_and(["python", "rust"]) == set()


def test_query_terms_are_stemmed_to_match_index():
    search = BooleanSearch(_build_sample_index())
    result_a = search.search_and(["Programming"])
    result_b = search.search_and(["program"])
    assert result_a == result_b == {1, 3, 4}


def test_evaluate_combined_query():
    search = BooleanSearch(_build_sample_index())
    query = [("OR", "programming"), ("AND", "language"), ("NOT", "java")]
    assert search.evaluate(query) == {1, 4}


def test_empty_query_returns_empty_set():
    search = BooleanSearch(_build_sample_index())
    assert search.search_and([]) == set()
    assert search.search_or([]) == set()
    assert search.evaluate([]) == set()