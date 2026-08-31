from search_engine.core.index.inverted_index import InvertedIndex
from search_engine.core.preprocessing.pipeline import Pipeline
from search_engine.performance.parallel_indexer import build_index_parallel

def _generate_raw_text_corpus(num_docs: int, words_per_doc: int = 50, seed: int = 42) -> dict[int, str]:
    import random

    vocab = [f"word{i}" for i in range(200)]
    rng = random.Random(seed)
    return {
        doc_id: " ".join(rng.choice(vocab) for _ in range(words_per_doc))
        for doc_id in range(num_docs)
    }

def test_parallel_index_matches_sequential_pipeline_exactly():
    raw_docs = _generate_raw_text_corpus(num_docs=100, words_per_doc=30, seed=5)

    pipeline = Pipeline()
    sequential = InvertedIndex()
    for doc_id, text in raw_docs.items():
        sequential.add_document(doc_id, pipeline.process(text))

    parallel = build_index_parallel(raw_docs, num_workers=2)

    assert parallel.document_count == sequential.document_count
    assert parallel.vocabulary_size == sequential.vocabulary_size
    for term in sequential.all_terms():
        assert parallel.get_postings(term) == sequential.get_postings(term)
    for doc_id in sequential.all_document_ids():
        assert parallel.document_length(doc_id) == sequential.document_length(doc_id)

def test_parallel_index_with_more_workers_than_documents():
    raw_docs = _generate_raw_text_corpus(num_docs=3, words_per_doc=10, seed=1)
    result = build_index_parallel(raw_docs, num_workers=8)
    assert result.document_count == 3

def test_parallel_index_empty_corpus():
    result = build_index_parallel({}, num_workers=2)
    assert result.document_count == 0

def test_parallel_index_single_document():
    raw_docs = {1: "python search engine"}
    result = build_index_parallel(raw_docs, num_workers=4)
    assert result.document_count == 1
    assert result.get_postings("python") == {1: [0]}

def test_parallel_index_applies_real_preprocessing():
    raw_docs = {1: "The Searching Engines"}
    result = build_index_parallel(raw_docs, num_workers=1)
    assert "search" in result.all_terms()
    assert "the" not in result.all_terms()

def test_parallel_index_with_explicit_chunk_size():
    raw_docs = _generate_raw_text_corpus(num_docs=50, words_per_doc=15, seed=3)
    result = build_index_parallel(raw_docs, num_workers=3, chunk_size=7)
    assert result.document_count == 50