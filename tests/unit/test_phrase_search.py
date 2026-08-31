from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.core.query.phrase_search import PhraseSearch


def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    pipeline = Pipeline()
    docs = {
        1: "the quick brown fox jumps over the lazy dog",
        2: "a quick fox and a brown bear were seen together",
        3: "the lazy dog and the quick brown fox are friends",
    }
    for doc_id, text in docs.items():
        index.add_document(doc_id, pipeline.process(text))
    return index


def test_exact_phrase_matches():
    search = PhraseSearch(_build_sample_index())
    assert search.search("quick brown") == {1, 3}


def test_word_order_matters():
    search = PhraseSearch(_build_sample_index())
    assert search.search("brown quick") == set()


def test_phrase_at_different_positions_in_different_docs():
    search = PhraseSearch(_build_sample_index())
    assert search.search("lazy dog") == {1, 3}


def test_three_word_phrase():
    search = PhraseSearch(_build_sample_index())
    assert search.search("brown bear seen") == {2}


def test_single_word_phrase_behaves_like_plain_lookup():
    search = PhraseSearch(_build_sample_index())
    assert search.search("fox") == {1, 2, 3}


def test_phrase_not_found_anywhere():
    search = PhraseSearch(_build_sample_index())
    assert search.search("purple elephant") == set()


def test_empty_phrase_returns_empty_set():
    search = PhraseSearch(_build_sample_index())
    assert search.search("") == set()
    assert search.search("the a an") == set()


def test_known_limitation_stopword_removal_creates_false_adjacency():
    search = PhraseSearch(_build_sample_index())
    assert 2 in search.search("fox brown")