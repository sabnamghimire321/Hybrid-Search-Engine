import pytest

from search_engine.core.index.inverted_index import InvertedIndex

def test_add_and_get_postings():
    idx = InvertedIndex()
    idx.add_document(1, ["python", "search", "engine"])
    idx.add_document(2, ["python", "web", "framework"])

    assert idx.get_postings("python") == {1: [0], 2: [0]}
    assert idx.get_postings("search") == {1: [1]}
    assert idx.get_postings("nonexistent") == {}

def test_positions_recorded_correctly_for_repeated_terms():
    idx = InvertedIndex()
    idx.add_document(1, ["python", "is", "great", "python", "rocks"])
    assert idx.get_postings("python") == {1: [0, 3]}

def test_document_frequency_counts_distinct_documents():
    idx = InvertedIndex()
    idx.add_document(1, ["python", "code"])
    idx.add_document(2, ["python", "rust"])
    idx.add_document(3, ["java", "code"])

    assert idx.document_frequency("python") == 2
    assert idx.document_frequency("code") == 2
    assert idx.document_frequency("java") == 1
    assert idx.document_frequency("nonexistent") == 0

def test_term_frequency_within_a_document():
    idx = InvertedIndex()
    idx.add_document(1, ["a", "b", "a", "a", "c"])
    assert idx.term_frequency("a", 1) == 3
    assert idx.term_frequency("b", 1) == 1
    assert idx.term_frequency("nonexistent", 1) == 0

def test_document_length_and_counts():
    idx = InvertedIndex()
    idx.add_document(1, ["a", "b", "c"])
    idx.add_document(2, ["x", "y"])
    assert idx.document_length(1) == 3
    assert idx.document_length(2) == 2
    assert idx.document_count == 2
    assert idx.vocabulary_size == 5

def test_get_document_ids_returns_a_set():
    idx = InvertedIndex()
    idx.add_document(1, ["python"])
    idx.add_document(2, ["python"])
    idx.add_document(3, ["rust"])

    assert idx.get_document_ids("python") == {1, 2}
    assert idx.get_document_ids("rust") == {3}
    assert idx.get_document_ids("nonexistent") == set()

def test_rejects_reindexing_same_doc_id():
    idx = InvertedIndex()
    idx.add_document(1, ["hello"])
    with pytest.raises(ValueError):
        idx.add_document(1, ["world"])

def test_remove_document_clears_its_postings():
    idx = InvertedIndex()
    idx.add_document(1, ["python", "search"])
    idx.add_document(2, ["python", "java"])

    assert idx.remove_document(1) is True
    assert idx.get_postings("search") == {}
    assert idx.get_document_ids("python") == {2}
    assert idx.document_count == 1

def test_remove_document_deletes_term_entirely_when_no_docs_left():
    idx = InvertedIndex()
    idx.add_document(1, ["unique_word"])
    idx.remove_document(1)

    assert "unique_word" not in idx.all_terms()

def test_remove_nonexistent_document_returns_false():
    idx = InvertedIndex()
    idx.add_document(1, ["hello"])
    assert idx.remove_document(999) is False
    assert idx.document_count == 1

def test_update_document_replaces_content_without_duplicating():
    idx = InvertedIndex()
    idx.add_document(1, ["old", "stale", "content"])
    idx.update_document(1, ["fresh", "new", "words"])

    assert idx.document_frequency("old") == 0
    assert idx.document_frequency("stale") == 0
    assert idx.document_frequency("fresh") == 1
    assert idx.document_count == 1

def test_update_document_works_even_if_doc_id_is_new():
    idx = InvertedIndex()
    idx.update_document(5, ["brand", "new"])
    assert idx.document_frequency("brand") == 1
    assert idx.document_count == 1

def test_bulk_load_reconstructs_full_index_state():
    idx = InvertedIndex()
    postings = {
        "python": {1: [0, 2], 2: [1]},
        "java": {2: [0]},
    }
    doc_lengths = {1: 3, 2: 2}

    idx.bulk_load(postings, doc_lengths)

    assert idx.document_count == 2
    assert idx.get_postings("python") == {1: [0, 2], 2: [1]}
    assert idx.term_frequency("python", 1) == 2
    assert idx.document_length(1) == 3
    assert idx.document_terms(1) == {"python"}
    assert idx.document_terms(2) == {"python", "java"}
    assert idx.all_document_ids() == {1, 2}