import math

import pytest

from search_engine.ranking.cosine_similarity import cosine_similarity
from search_engine.semantic.embeddings import (
    HashEmbeddingProvider,
    PrecomputedEmbeddingProvider,
    SentenceTransformerProvider,
)

def test_hash_provider_returns_correct_dimension():
    provider = HashEmbeddingProvider(dimension=32)
    vector = provider.embed("python search engine")
    assert len(vector) == 32
    assert provider.dimension == 32

def test_hash_provider_is_deterministic():
    provider = HashEmbeddingProvider()
    v1 = provider.embed("machine learning is great")
    v2 = provider.embed("machine learning is great")
    assert v1 == v2

def test_hash_provider_empty_text_returns_zero_vector():
    provider = HashEmbeddingProvider(dimension=16)
    vector = provider.embed("")
    assert vector == [0.0] * 16

def test_hash_provider_vector_is_normalized():
    provider = HashEmbeddingProvider()
    vector = provider.embed("some sample text with several distinct words")
    magnitude = math.sqrt(sum(x * x for x in vector))
    assert math.isclose(magnitude, 1.0, abs_tol=1e-9)

def test_hash_provider_similar_texts_are_more_similar_than_different_ones():
    provider = HashEmbeddingProvider()

    vec_a = provider.embed("python programming language search engine")
    vec_b = provider.embed("python programming language web framework")
    vec_c = provider.embed("cooking recipes italian pasta dinner")

    dict_a = {str(i): v for i, v in enumerate(vec_a)}
    dict_b = {str(i): v for i, v in enumerate(vec_b)}
    dict_c = {str(i): v for i, v in enumerate(vec_c)}

    sim_ab = cosine_similarity(dict_a, dict_b)
    sim_ac = cosine_similarity(dict_a, dict_c)

    assert sim_ab > sim_ac

def test_precomputed_provider_looks_up_by_key():
    embeddings = {"doc1": [0.1, 0.2, 0.3], "doc2": [0.4, 0.5, 0.6]}
    provider = PrecomputedEmbeddingProvider(embeddings)

    assert provider.embed("doc1") == [0.1, 0.2, 0.3]
    assert provider.dimension == 3

def test_precomputed_provider_missing_key_raises():
    provider = PrecomputedEmbeddingProvider({"doc1": [0.1, 0.2]})
    with pytest.raises(KeyError):
        provider.embed("nonexistent")

def test_precomputed_provider_empty_dict_raises():
    with pytest.raises(ValueError):
        PrecomputedEmbeddingProvider({})

def test_precomputed_provider_loads_from_json_file(tmp_path):
    import json

    path = tmp_path / "embeddings.json"
    data = {"doc1": [0.1, 0.2, 0.3], "doc2": [0.4, 0.5, 0.6]}
    path.write_text(json.dumps(data))

    provider = PrecomputedEmbeddingProvider.from_json_file(str(path))
    assert provider.embed("doc2") == [0.4, 0.5, 0.6]
    assert provider.dimension == 3

def test_sentence_transformer_provider_raises_helpful_error_when_unavailable():
    try:
        SentenceTransformerProvider()
        pytest.skip("sentence-transformers is fully installed and working in this environment")
    except ImportError as exc_info:
        message = str(exc_info)
        assert "HashEmbeddingProvider" in message
        assert "PrecomputedEmbeddingProvider" in message