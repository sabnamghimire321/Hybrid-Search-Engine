import math

from search_engine.semantic.vector_index import VectorIndex

def test_search_finds_closest_vector():
    index = VectorIndex()
    index.add(1, [1.0, 0.0, 0.0])
    index.add(2, [0.0, 1.0, 0.0])
    index.add(3, [0.9, 0.1, 0.0])

    results = index.search([1.0, 0.0, 0.0], top_k=3)
    doc_ids_in_order = [doc_id for doc_id, _ in results]

    assert doc_ids_in_order[0] == 1
    assert doc_ids_in_order[1] == 3

def test_search_respects_top_k():
    index = VectorIndex()
    for i in range(10):
        index.add(i, [float(i), 1.0, 1.0])

    results = index.search([5.0, 1.0, 1.0], top_k=3)
    assert len(results) == 3

def test_top_k_matches_full_sort_when_smaller_than_corpus():
    index = VectorIndex()
    for i in range(20):
        index.add(i, [float(i % 7), float(i % 3), float(i % 5)])

    full = index.search([3.0, 1.0, 2.0], top_k=20)
    top5 = index.search([3.0, 1.0, 2.0], top_k=5)

    assert top5 == full[:5]

def test_identical_vector_has_similarity_one():
    index = VectorIndex()
    index.add(1, [0.5, 0.5, 0.7071])

    results = index.search([0.5, 0.5, 0.7071], top_k=1)
    assert math.isclose(results[0][1], 1.0, abs_tol=1e-3)

def test_orthogonal_vectors_have_similarity_zero():
    index = VectorIndex()
    index.add(1, [1.0, 0.0])
    index.add(2, [0.0, 1.0])

    results = index.search([1.0, 0.0], top_k=2)
    result_dict = dict(results)
    assert math.isclose(result_dict[1], 1.0, abs_tol=1e-9)
    assert math.isclose(result_dict[2], 0.0, abs_tol=1e-9)

def test_empty_index_returns_empty_list():
    index = VectorIndex()
    assert index.search([1.0, 0.0], top_k=5) == []

def test_add_overwrites_existing_doc_id():
    index = VectorIndex()
    index.add(1, [1.0, 0.0])
    index.add(1, [0.0, 1.0])

    assert index.get(1) == [0.0, 1.0]
    assert len(index) == 1

def test_remove_and_contains():
    index = VectorIndex()
    index.add(1, [1.0, 0.0])

    assert 1 in index
    assert index.remove(1) is True
    assert 1 not in index
    assert index.remove(1) is False

def test_all_doc_ids():
    index = VectorIndex()
    index.add(1, [1.0])
    index.add(2, [2.0])
    assert set(index.all_doc_ids()) == {1, 2}

def test_search_with_zero_vector_query_returns_zero_similarity_for_all():
    index = VectorIndex()
    index.add(1, [1.0, 2.0])
    index.add(2, [3.0, 4.0])

    results = index.search([0.0, 0.0], top_k=2)
    assert all(math.isclose(sim, 0.0) for _, sim in results)