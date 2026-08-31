from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.storage.serialization import (
    MAGIC,
    VERSION,
    deserialize_index,
    serialize_index,
)

def _build_sample_index() -> InvertedIndex:
    index = InvertedIndex()
    index.add_document(1, ["python", "search", "engine", "python"])
    index.add_document(2, ["python", "web", "framework"])
    index.add_document(3, ["java", "enterprise"])
    return index

def test_serialize_produces_bytes_with_correct_magic_header():
    index = _build_sample_index()
    data = serialize_index(index)
    assert data[0:4] == MAGIC
    assert isinstance(data, bytes)

def test_roundtrip_preserves_document_count_and_lengths():
    index = _build_sample_index()
    data = serialize_index(index)
    restored = deserialize_index(data)

    assert restored.document_count == index.document_count
    for doc_id in index.all_document_ids():
        assert restored.document_length(doc_id) == index.document_length(doc_id)

def test_roundtrip_preserves_postings_exactly():
    index = _build_sample_index()
    data = serialize_index(index)
    restored = deserialize_index(data)

    for term in index.all_terms():
        assert restored.get_postings(term) == index.get_postings(term)

def test_roundtrip_preserves_document_frequency_and_term_frequency():
    index = _build_sample_index()
    restored = deserialize_index(serialize_index(index))

    for term in index.all_terms():
        assert restored.document_frequency(term) == index.document_frequency(term)
    for doc_id in index.all_document_ids():
        for term in index.document_terms(doc_id):
            assert restored.term_frequency(term, doc_id) == index.term_frequency(term, doc_id)

def test_roundtrip_preserves_document_terms():
    index = _build_sample_index()
    restored = deserialize_index(serialize_index(index))

    for doc_id in index.all_document_ids():
        assert restored.document_terms(doc_id) == index.document_terms(doc_id)

def test_deserialize_rejects_bad_magic_bytes():
    garbage = b"XXXX" + b"\x00" * 20
    try:
        deserialize_index(garbage)
        assert False, "should have raised ValueError"
    except ValueError as e:
        assert "magic bytes" in str(e)

def test_deserialize_rejects_unsupported_version():
    import struct

    bad_version_data = MAGIC + struct.pack("<I", VERSION + 999) + struct.pack("<I", 0) + struct.pack(
        "<I", 0
    )
    try:
        deserialize_index(bad_version_data)
        assert False, "should have raised ValueError"
    except ValueError as e:
        assert "version" in str(e)

def test_empty_index_roundtrips_cleanly():
    index = InvertedIndex()
    restored = deserialize_index(serialize_index(index))
    assert restored.document_count == 0
    assert restored.vocabulary_size == 0

def test_serialized_size_scales_with_content_not_wastefully_large():
    index = _build_sample_index()
    data = serialize_index(index)
    assert len(data) < 1000