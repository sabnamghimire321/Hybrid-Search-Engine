import math

from search_engine.ranking.cosine_similarity import (
    cosine_similarity,
    dot_product,
    magnitude,
)

def test_identical_vectors_have_similarity_one():
    v = {"python": 2.0, "search": 1.5}
    assert math.isclose(cosine_similarity(v, v), 1.0)

def test_orthogonal_vectors_have_similarity_zero():
    a = {"python": 1.0, "rust": 1.0}
    b = {"java": 1.0, "cobol": 1.0}
    assert cosine_similarity(a, b) == 0.0

def test_zero_vector_returns_zero_not_a_crash():
    empty = {}
    normal = {"python": 1.0}
    assert cosine_similarity(empty, normal) == 0.0
    assert cosine_similarity(empty, empty) == 0.0

def test_scaling_a_vector_does_not_change_similarity():
    short_doc = {"python": 1.0, "search": 2.0}
    long_doc = {"python": 5.0, "search": 10.0}  
    assert math.isclose(cosine_similarity(short_doc, long_doc), 1.0)

def test_partial_overlap_gives_intermediate_value():
    a = {"python": 1.0, "search": 1.0}
    b = {"python": 1.0, "java": 1.0}
    expected = 1.0 / (math.sqrt(2) * math.sqrt(2))
    result = cosine_similarity(a, b)
    assert math.isclose(result, expected)
    assert 0.0 < result < 1.0

def test_dot_product_direct():
    a = {"x": 2.0, "y": 3.0}
    b = {"x": 4.0, "y": 1.0, "z": 100.0}
    assert dot_product(a, b) == 2.0 * 4.0 + 3.0 * 1.0

def test_magnitude_direct():
    v = {"x": 3.0, "y": 4.0}
    assert magnitude(v) == 5.0