import pytest

from search_engine.storage.mmap_store import MAGIC, MmapIndexReader, write_mmap_index

def _sample_data():
    doc_lengths = {1: 4, 2: 3, 3: 2}
    term_postings = {
        "python": {1: [0, 3], 2: [0]},
        "search": {1: [1]},
        "java": {3: [0]},
    }
    return doc_lengths, term_postings

def test_write_creates_file_with_correct_magic(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    assert path.exists()
    assert path.read_bytes()[0:4] == MAGIC

def test_reader_retrieves_correct_postings_per_term(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        assert reader.get_postings("python") == {1: [0, 3], 2: [0]}
        assert reader.get_postings("search") == {1: [1]}
        assert reader.get_postings("java") == {3: [0]}

def test_reader_retrieves_document_lengths(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        assert reader.document_length(1) == 4
        assert reader.document_length(2) == 3
        assert reader.document_count == 3
        assert reader.vocabulary_size == 3

def test_unseen_term_returns_empty_dict(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        assert reader.get_postings("nonexistent") == {}

def test_lookups_work_in_any_order_and_repeatedly(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        assert reader.get_postings("java") == {3: [0]}
        assert reader.get_postings("python") == {1: [0, 3], 2: [0]}
        assert reader.get_postings("java") == {3: [0]}
        assert reader.get_postings("search") == {1: [1]}

def test_bad_magic_bytes_raises(tmp_path):
    path = tmp_path / "bad.mmap"
    path.write_bytes(b"NOPE" + b"\x00" * 30)

    with pytest.raises(ValueError):
        MmapIndexReader(str(path))

def test_context_manager_closes_cleanly(tmp_path):
    doc_lengths, term_postings = _sample_data()
    path = tmp_path / "index.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        reader.get_postings("python")
    assert True

def test_larger_corpus_all_terms_retrievable(tmp_path):
    doc_lengths = {i: 10 for i in range(50)}
    term_postings = {
        f"term{i}": {j: [0, 1] for j in range(i % 10, i % 10 + 5)} for i in range(200)
    }
    path = tmp_path / "big.mmap"
    write_mmap_index(doc_lengths, term_postings, str(path))

    with MmapIndexReader(str(path)) as reader:
        assert reader.vocabulary_size == 200
        assert reader.document_count == 50
        for term, expected_postings in term_postings.items():
            assert reader.get_postings(term) == expected_postings