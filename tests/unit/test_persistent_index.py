import pytest

from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.storage.persistent_index import PersistentIndexStore

def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.add_document(1, ["python", "search", "engine"])
    index.add_document(2, ["java", "programming"])
    return index

def test_save_creates_a_file(tmp_path):
    index = _build_sample_index()
    store = PersistentIndexStore()
    path = tmp_path / "index.bin"

    store.save(index, str(path))
    assert path.exists()
    assert path.stat().st_size > 0

def test_save_then_load_roundtrips_correctly(tmp_path):
    index = _build_sample_index()
    store = PersistentIndexStore()
    path = tmp_path / "index.bin"

    store.save(index, str(path))
    restored = store.load(str(path))

    assert restored.document_count == index.document_count
    assert restored.get_postings("python") == index.get_postings("python")
    assert restored.document_terms(1) == index.document_terms(1)

def test_load_missing_file_raises_file_not_found(tmp_path):
    store = PersistentIndexStore()
    with pytest.raises(FileNotFoundError):
        store.load(str(tmp_path / "does_not_exist.bin"))

def test_load_corrupted_file_raises_value_error(tmp_path):
    store = PersistentIndexStore()
    path = tmp_path / "corrupted.bin"
    path.write_bytes(b"not a valid index file at all")

    with pytest.raises(ValueError):
        store.load(str(path))

def test_exists_reflects_file_presence(tmp_path):
    store = PersistentIndexStore()
    path = tmp_path / "index.bin"

    assert store.exists(str(path)) is False
    store.save(_build_sample_index(), str(path))
    assert store.exists(str(path)) is True

def test_overwriting_an_existing_index_file(tmp_path):
    store = PersistentIndexStore()
    path = tmp_path / "index.bin"

    store.save(_build_sample_index(), str(path))

    new_index = InvertedIndex()
    new_index.add_document(99, ["completely", "different"])
    store.save(new_index, str(path))

    restored = store.load(str(path))
    assert restored.document_count == 1
    assert restored.get_document_ids("completely") == {99}
    assert restored.get_document_ids("python") == set()